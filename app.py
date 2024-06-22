from flask import Flask, request, render_template, jsonify
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definición del lexer
tokens = (
    'INT', 'FLOAT', 'STRING', 'SEMICOLON', 'ID', 'EQUALS', 'NUMBER', 'FLOAT_NUMBER',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
    'AND', 'PLUS', 'PLUSPLUS', 'MULTIPLY', 'COMMA', 'FOR', 'IN', 'RANGE', 'WHILE',
    'DO', 'ENDDO', 'ENDWHILE', 'IF', 'INPUT', 'STRING_LITERAL'
)

t_ignore = ' \t'
t_SEMICOLON = r';'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_GT = r'>'
t_LT = r'<'
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='
t_NE = r'!='
t_AND = r'and'
t_PLUS = r'\+'
t_PLUSPLUS = r'\+\+'
t_MULTIPLY = r'\*'
t_COMMA = r','

def t_DO(t):
    r'DO'
    return t

def t_ENDDO(t):
    r'ENDDO'
    return t

def t_ENDWHILE(t):
    r'ENDWHILE'
    return t

def t_IF(t):
    r'if'
    return t

def t_INPUT(t):
    r'input'
    return t

def t_INT(t):
    r'int'
    return t

def t_FLOAT(t):
    r'float'
    return t

def t_STRING(t):
    r'string'
    return t

def t_FOR(t):
    r'for'
    return t

def t_WHILE(t):
    r'while'
    return t

def t_IN(t):
    r'in'
    return t

def t_RANGE(t):
    r'range'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_FLOAT_NUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = str(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# Definición del parser
variables = {}
initial_values = {}
errors = []
syntax_errors = []

def p_program(p):
    '''program : statement_list'''
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    pass

def p_statement(p):
    '''statement : declaration
                 | assignment
                 | if_statement
                 | while_statement
                 | do_while_statement
                 | for_statement
                 | input_statement
                 | block'''
    pass

def p_declaration(p):
    '''declaration : INT ID EQUALS NUMBER SEMICOLON
                   | FLOAT ID EQUALS FLOAT_NUMBER SEMICOLON
                   | STRING ID EQUALS STRING_LITERAL SEMICOLON'''
    var_name = p[2]
    var_type = p[1]
    if var_name in variables:
        errors.append(f"Línea {p.lineno(1)}: La variable '{var_name}' ya está declarada.")
    else:
        if var_type == 'int' and isinstance(p[4], int):
            variables[var_name] = 'int'
            initial_values[var_name] = p[4]
        elif var_type == 'float' and isinstance(p[4], float):
            variables[var_name] = 'float'
            initial_values[var_name] = p[4]
        elif var_type == 'string' and isinstance(p[4], str):
            variables[var_name] = 'string'
            initial_values[var_name] = p[4]
        else:
            errors.append(f"Línea {p.lineno(1)}: Tipo de dato incorrecto para la variable '{var_name}'.")

def p_declaration_error_int(p):
    '''declaration : INT ID EQUALS FLOAT_NUMBER SEMICOLON
                   | INT ID EQUALS STRING_LITERAL SEMICOLON'''
    errors.append(f"Línea {p.lineno(1)}: No se puede asignar un valor de tipo float o string a la variable '{p[2]}' de tipo int.")

def p_declaration_error_float(p):
    '''declaration : FLOAT ID EQUALS NUMBER SEMICOLON
                   | FLOAT ID EQUALS STRING_LITERAL SEMICOLON'''
    errors.append(f"Línea {p.lineno(1)}: No se puede asignar un valor de tipo int o string a la variable '{p[2]}' de tipo float.")

def p_declaration_error_string(p):
    '''declaration : STRING ID EQUALS NUMBER SEMICOLON
                   | STRING ID EQUALS FLOAT_NUMBER SEMICOLON'''
    errors.append(f"Línea {p.lineno(1)}: No se puede asignar un valor de tipo int o float a la variable '{p[2]}' de tipo string.")

def p_assignment(p):
    '''assignment : ID EQUALS expression SEMICOLON
                  | ID PLUSPLUS SEMICOLON'''
    var_name = p[1]
    if var_name not in variables:
        errors.append(f"Línea {p.lineno(1)}: La variable '{var_name}' usada en la asignación no está declarada.")
    elif p[2] == '++' and variables[var_name] != 'int':
        errors.append(f"Línea {p.lineno(1)}: Operación no válida para la variable '{var_name}' de tipo {variables[var_name]}.")
    elif p[2] == '=':
        expr_value, expr_type = p[3]
        if expr_type != variables[var_name]:
            errors.append(f"Línea {p.lineno(1)}: No se puede asignar un valor de tipo {expr_type} a la variable '{var_name}' de tipo {variables[var_name]}.")

def p_expression(p):
    '''expression : NUMBER
                  | FLOAT_NUMBER
                  | STRING_LITERAL
                  | ID
                  | expression MULTIPLY expression
                  | expression PLUS expression'''
    if len(p) == 2:
        if isinstance(p[1], int):
            p[0] = (p[1], 'int')
        elif isinstance(p[1], float):
            p[0] = (p[1], 'float')
        elif isinstance(p[1], str):
            p[0] = (p[1], 'string')
        elif p[1] in variables:
            p[0] = (initial_values[p[1]], variables[p[1]])
        else:
            errors.append(f"Línea {p.lineno(1)}: La variable '{p[1]}' no está declarada.")
            p[0] = (p[1], 'undefined')
    elif len(p) == 4:
        if p[1][1] == 'float' and p[3][1] == 'float':
            p[0] = (p[1][0] * p[3][0], 'float')
        elif p[1][1] == 'int' and p[3][1] == 'int':
            p[0] = (p[1][0] * p[3][0], 'int')
        else:
            errors.append(f"Línea {p.lineno(1)}: No se puede multiplicar valores de tipo {p[1][1]} y {p[3][1]}.")
            p[0] = (None, 'error')

def p_input_statement(p):
    '''input_statement : INPUT LPAREN expression RPAREN SEMICOLON'''
    if p[3][1] != 'string':
        errors.append(f"Línea {p.lineno(1)}: La función 'input' solo acepta valores de tipo string.")

def p_if_statement(p):
    '''if_statement : IF LPAREN condition RPAREN block'''
    pass

def p_while_statement(p):
    '''while_statement : WHILE LPAREN condition RPAREN block'''
    pass

def p_do_while_statement(p):
    '''do_while_statement : DO statement_list ENDDO WHILE LPAREN condition RPAREN ENDWHILE'''
    pass

def p_for_statement(p):
    '''for_statement : FOR LPAREN ID IN RANGE LPAREN NUMBER COMMA NUMBER RPAREN RPAREN block'''
    pass

def p_condition(p):
    '''condition : expression EQ expression
                 | expression NE expression
                 | expression GT expression
                 | expression LT expression
                 | expression GE expression
                 | expression LE expression
                 | condition AND condition'''
    pass

def p_block(p):
    '''block : LBRACE statement_list RBRACE'''
    pass

def p_error(p):
    if p:
        syntax_errors.append(f"Error de sintaxis en '{p.value}' en la línea {p.lineno}")
    else:
        syntax_errors.append("Error de sintaxis al final del archivo")

parser = yacc.yacc()

def perform_lexical_analysis(code):
    lexer.input(code)
    token_list = []
    totals = {'Reservada': 0, 'Identificador': 0, 'Número': 0, 'Símbolo': 0, 'String': 0, 'Error': 0}
    while True:
        tok = lexer.token()
        if not tok:
            break
        category = categorize_token(tok.type)
        token_list.append({
            'value': tok.value,
            'type': tok.type,
            'category': category
        })
        totals[category] += 1
    return token_list, totals

def categorize_token(token_type):
    if token_type in ['INT', 'FLOAT', 'STRING', 'FOR', 'WHILE', 'DO', 'ENDDO', 'ENDWHILE', 'IF', 'IN', 'RANGE', 'INPUT']:
        return 'Reservada'
    elif token_type == 'ID':
        return 'Identificador'
    elif token_type in ['NUMBER', 'FLOAT_NUMBER']:
        return 'Número'
    elif token_type in ['SEMICOLON', 'EQUALS', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE', 'AND', 'PLUS', 'PLUSPLUS', 'MULTIPLY', 'COMMA']:
        return 'Símbolo'
    elif token_type == 'STRING_LITERAL':
        return 'String'
    else:
        return 'Error'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    global variables, errors, syntax_errors
    code = request.form['code']
    if not code:
        return jsonify({"error": "No se proporcionó código"}), 400

    variables = {}
    initial_values = {}
    errors = []
    syntax_errors = []
    lexer.lineno = 1

    # Análisis léxico
    token_list, totals = perform_lexical_analysis(code)

    # Análisis sintáctico y semántico
    parser.parse(code)

    if not errors and not syntax_errors:
        return jsonify({"message": "El código es correcto", "lexical": token_list, "totals": totals, "syntax_errors": [], "semantic_errors": []}), 200
    else:
        return jsonify({"errors": errors, "lexical": token_list, "totals": totals, "syntax_errors": syntax_errors, "semantic_errors": errors}), 200

if __name__ == '__main__':
    app.run(debug=True)