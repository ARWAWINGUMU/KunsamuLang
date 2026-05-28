grammar KunsamuLang;

program
    : comunidad+ EOF
    ;

comunidad
    : COMUNIDAD STRING LBRACE comunidadBody* RBRACE
    ;

comunidadBody
    : territorio
    | proyecto
    | participante
    | actividad
    | attribute
    ;

territorio
    : TERRITORIO STRING LBRACE territorioBody* RBRACE
    ;

territorioBody
    : elemento
    | mensaje
    | attribute
    ;

elemento
    : ELEMENTO STRING LBRACE elementoBody* RBRACE
    ;

elementoBody
    : mensaje
    | attribute
    ;

proyecto
    : PROYECTO STRING LBRACE proyectoBody* RBRACE
    ;

proyectoBody
    : curso
    | participante
    | actividad
    | attribute
    ;

curso
    : CURSO STRING LBRACE cursoBody* RBRACE
    ;

cursoBody
    : duracion
    | enfoque
    | participante
    | actividad
    | attribute
    ;

participante
    : PARTICIPANTE STRING LBRACE attribute* RBRACE
    ;

actividad
    : ACTIVIDAD STRING LBRACE attribute* RBRACE
    ;

mensaje
    : MENSAJE COLON value
    ;

duracion
    : DURACION COLON NUMBER ID
    ;

enfoque
    : ENFOQUE COLON ID
    ;

attribute
    : ID COLON value
    ;

value
    : STRING
    | NUMBER ID?
    | ID
    | list
    ;

list
    : LBRACK value (COMMA value)* RBRACK
    ;

COMUNIDAD: 'COMUNIDAD';
TERRITORIO: 'TERRITORIO';
ELEMENTO: 'ELEMENTO';
MENSAJE: 'MENSAJE';
PROYECTO: 'PROYECTO';
CURSO: 'CURSO';
DURACION: 'DURACION';
ENFOQUE: 'ENFOQUE';
PARTICIPANTE: 'PARTICIPANTE';
ACTIVIDAD: 'ACTIVIDAD';

LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
COLON: ':';
COMMA: ',';

STRING: '"' (ESC | ~["\\])* '"';
NUMBER: [0-9]+ ('.' [0-9]+)?;
ID: [a-zA-Z_áéíóúÁÉÍÓÚñÑ][a-zA-Z0-9_áéíóúÁÉÍÓÚñÑ-]*;

fragment ESC: '\\' ["\\/bfnrt];

LINE_COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
WS: [ \t\r\n]+ -> skip;
