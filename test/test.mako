%! inherit file="base.html"
<%
    rows = [[v for v in range(0,10)] for row in range(0,10)]
%>
html
    head
        title | lalala
        script
            <!--
            {%
            x = 1;
            function b()
            {
                x = 3;
            }
x = 4;
            %}
            -->

    body
        form action="lala" method=post
            input#first name=x value=""

            input

        %if a > b:
            ${mytag}#table1.class1
                | ${makerow(row)}
        %else:
            | no content

        #content
            table#maintable
                % for row in rows:
                    tr
                        td | ${makerow(row)}
                        td
                            .status.big|lala
        p#lala > small.red > a href="yes" | lala
        p#lala>small.red>a href="yes" > b
            |lala

           
%! def name="makerow(row)"
    tr.row
        % for name in row:
            td.td1.td${name} | ${name}

