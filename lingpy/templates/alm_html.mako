<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>${shorttitle}</title>
        <style>
<%include file="alm.css"/>
        </style>
        <script type="text/javascript">
            var myjson = ${json.dumps(jsondata, indent=1)};
<%include file="alm.js"/>
        </script>
    </head>
    <body>
        <h3 align="left">${title}</h3>
        <h4 align="left">Dataset: ${dataset}</h4>
        <div id="display" class="display"></div>
        <table align="left" style='border:0;background-color:#b9d9f2;'>


            % if confidence:
            <table id="{NAME}" style="background-color:#b9d9f2;border:0">
                <tr style="background-color:#2f95e3;border:0" id="xxx{NAME}">
                    <td colspan="3"><b>Concept: <i>{NAME}</i> (ID: {ID})</b></td><td>
                    <input class="mybut" type="button" onclick="color('sound_classes', '{NAME}');" value="Sound Classes" />
                    <input class="mybut" type="button" onclick="color('confidence', '{NAME}');" value="Confidence" />
                    <input class="mybut" type="button" onclick="color('scores', '{NAME}');" value="Scores" />
                </td>
                </tr>
            % else:
                <tr style="background-color:#2f95e3;border:0">
                    <td colspan="4"><b>Concept: <i>{NAME}</i> (ID: {ID})</b></td>
                </tr>
            % endif
            <tr>
                <td><b>CogID</b></td>
                <td><b>Language</b></td>
                <td><b>Entry</b></td>
                <td><b>Aligned Entry</b></td>
            </tr>

            % for index, row in enumerate(m):
            <tr class="${colors[abs(int(row[0]))]} ${'loan' if int(row[0]) < 0 else ''} taxon" taxon="${row[1]}">
                <td>${row[0}</td>\n'.format(row[0])
                <td>${row[1].strip('.')}</td>\n'.format(label(row[1].strip('.')))
                <td>${''.join([cell.split('/')[0] for cell in row[4:]]).replace('-', '')}</td>
                <td class="${colors[abs(int(row[0]))]}">
                    <table class="${colors[abs(int(row[0]))]}">
                        <tr>
                            % if cognate_set(m, index):
                                % for char in row[4:]:
                                    ## check for confidence scores
                                    % if '/' in char:
                                        try:
                                            char, conf, num = char.split('/')
                                            conf = int(conf)
                                        except ValueError:
                                            print(char.split('/'))
                                            raise ValueError("Something is wrong with %s." % (char))
                                    % else:
                                        char, conf, rgb = char, (255, 255, 255), 0.0
                                    % endif
                                    % if char == '-':
                                        d = 'dolgo_GAP'
                                    % else:
                                        tc = token2class(char, rcParams['dolgo'])
                                        # bad check for three classes named differently
                                        d = 'dolgo_' + {'_': 'X', '1': 'TONE', '0': 'ERROR'}.get(tc, tc)
                                    % endif
                                    % if confidence:
                                        <td class="char ${d}" confidence=${conf} char="${char}" onclick="show('${num}')" num="${num}">
                                            ${char}
                                        </td>
                                    % else:
                                        <td class="char ${d}">${char}</td>
                                    % endif
                                % endfor
                            % else:
                            <td class="${colors[abs(int(l[0]))]}">--</td>
                            % endif
                        </tr>
                    </table>
                </td>
            </tr>
            % endfor

            % if confidence:
                </table>
            % endif
            <tr class="empty"><td colspan="4" class="empty">
            <hr class="empty" /></td></tr>
        </table>
    </body>
</html>
