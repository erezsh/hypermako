Hypermako is a mako-&-html generator inspired by haml (well, tecnhically, by shpaml).

It cleverly converts indented statements (like python's) into blocks of html and mako.

It requires Plyplus to run: https://github.com/erezsh/plyplus

Basic Example
--------------

The following code:
    %! inherit file="base.html"
    html
        head > title | Example
        body
            h2.blue | List of links

            ul#main_list
                %for i in rows:
                    li#item${i.id} > .inner
                        %if i.link:
                            a href="${i.link}" | ${i}
                        %else:
                            | ${i}              


Results in:
    <%inherit file="base.html"/>
    <html>
        <head>
        <title>
            Example
        </title>
        </head>
        <body>
            <h2 class="blue">
                List of links
            </h2>
            <ul id="main_list">
                %for i in rows:
                    <li id="item${i.id}">
                    <div class="inner">
                        %if i.link:
                            <a href="${i.link}">
                                ${i}
                            </a>
                        %else:
                            ${i}
                        %endif
                    </div>
                    </li>
                %endfor
            </ul>
        </body>
    </html>

See test/test.mako for a more complete demonstration of features
