start: block?;

block: (mako_line | hyper_line | (raw|text|hyper_verbatim) NEWLINE)+;

// TODO parse mako!
@mako_line:
    mako_meta_oneliner
    | mako_meta_block
    | mako_control_block
    | mako_code_block NEWLINE
    ;
    
mako_control_block: (mako_control_stmt NEWLINE INDENT block DEDENT)+;
mako_meta_block: mako_meta_stmt NEWLINE INDENT block DEDENT;
mako_meta_oneliner: mako_meta_stmt NEWLINE;
mako_code_block: '<%(.|\n)*?%>' ;

mako_control_stmt: '%[^\n]+' ;
mako_meta_stmt: '%![^\n]*' ;

hyper_line: (hyper_tagdecl|hyper_exprs) (NEWLINE | text NEWLINE | NEWLINE INDENT block DEDENT) ;
hyper_verbatim: '{%(.|\n)*?%}' ;

text: TEXT;

raw: '[<-][^%][^\n]*';    // TODO: parse mako
hyper_exprs: (hyper_expr|hyper_tagdecl) ('[\f \t]*>[\f \t]*' hyper_exprs)?;
//hyper_exprs: hyper_expr;
hyper_expr: hyper_tagdecl (WS hyper_tagattrs)?;

hyper_tagdecl:
      tag id? class*
    | id class*
    | class+
    ;

tag: name;
id: '\#' name;
class: '\.' name;

hyper_tagattrs: hyper_tagattr (WS hyper_tagattr)*;
hyper_tagattr: name WS? '=' WS? value;

name: NAME;   // TODO: parse mako
value: NAME | VALUE;   // TODO: there can be mako inside the string

NAME: '([a-zA-Z0-9_]|\${[^}\n]*?})+';
VALUE: '"[^\"\n]*?"';
TEXT: '[\t \f]*\|[^\n]*';

WS: '[\t \f]+';
NEWLINE: '(\r?\n[\t ]*)+' (%newline);

INDENT: '<INDENT>';
DEDENT: '<DEDENT>';

###
from indent_postlex import IndentTracker
self.lexer_postproc = IndentTracker
                                        
