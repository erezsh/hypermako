start: block?;

block: (mako_line | hyper_line | (raw|text|hyper_verbatim) NEWLINE)+;

// TODO parse mako!
mako_line:
    mako_meta_oneliner
    | mako_meta_block
    | mako_control_block
    | mako_code_block NEWLINE
    ;
    
mako_control_block: mako_control_stmt NEWLINE INDENT block DEDENT (mako_control_stmt2 NEWLINE INDENT block DEDENT)*;
mako_meta_block: mako_meta_stmt NEWLINE INDENT block DEDENT;
mako_meta_oneliner: mako_meta_stmt NEWLINE;
mako_code_block: MAKO_BLOCK ;

mako_control_stmt: mako_for_stmt | mako_if_stmt;
@mako_for_stmt: '%\s*for[^\n]+' ;
@mako_if_stmt: '%\s*if[^\n]+' ;
mako_control_stmt2: mako_elif_stmt | mako_else_stmt;
@mako_elif_stmt: '%\s*elif[^\n]+' ;
@mako_else_stmt: '%\s*else[^\n]+' ;

mako_meta_stmt: '%![^\n]*' ;

hyper_line: hyper_exprs (NEWLINE | text NEWLINE | NEWLINE INDENT block DEDENT) ;
hyper_verbatim: VERBATIM ;

text: TEXT;

raw: '[<-][^%][^\n]*';    // TODO: parse mako
hyper_exprs: hyper_expr ('>' hyper_exprs)?;
//hyper_exprs: hyper_expr;
hyper_expr: hyper_tagdecl hyper_tagattrs?;

hyper_tagdecl: HYPER_TAGDECL;
HYPER_TAGDECL: '([a-zA-Z0-9_#-]|\.|\${[^}\n]*?})+'
{
    start:
          tag id? class*
        | id class*
        | class+
        ;

    tag: name;
    id: '\#' name;
    class: '\.' name;
    name: NAME;   // TODO: parse mako
    NAME: '([a-zA-Z0-9_-]|\${[^}\n]*?})+';
};


@hyper_tagattrs: hyper_tagattr hyper_tagattr*;
hyper_tagattr: name '=' value | HYPER_TAGDECL;

name: HYPER_TAGDECL;   // TODO: parse mako
value: HYPER_TAGDECL | VALUE;   // TODO: there can be mako inside the string

VALUE: '"[^\"\n]*?"';
TEXT: '[\t \f]*\|[^\n]*';

WS: '[\t \f]+' (%ignore);
NEWLINE: '(\r?\n[\t ]*)+' (%newline);
VERBATIM: '{%(.|\n)*?%}' (%newline);
MAKO_BLOCK: '<%(.|\n)*?%>' (%newline);

INDENT: '<INDENT>';
DEDENT: '<DEDENT>';

###
from hypermako.indent_postlex import IndentTracker
self.lexer_postproc = IndentTracker
                                        
