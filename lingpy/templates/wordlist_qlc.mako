% if prettify:
# Wordlist
% endif
% if meta:
% if prettify:
# META
% endif
    % for k, v in sorted(meta.items(), key=lambda x: x[0]):
@${k}:${v}
    % endfor
% endif
% if taxa:
# TAXA
<taxa>
${taxa}
</taxa>
% endif
% if jsonpairs:
@json: ${json.dumps(jsonpairs)}
% endif
% if msapairs:
    % for ref in msapairs:
# MSA reference: ${ref}
        % for k, v in msapairs[ref].items():
#
<msa id="${k}" ref="${ref}"${' consensus="' + ' '.join(v['consensus']) + '"' if 'consensus' in v else ''}>
${msa2str(v, wordlist=True)}
</msa>
        % endfor
    % endfor
% endif
% if distances:
# DISTANCES
<dst>
${distances}
</dst>
% endif
% if trees:
# TREES
${trees}
    % for key, value in trees.items():
<tre id="${key}">
${value}
</tre>
    % endfor
% endif
% if scorer:
# SCORER
    % for key, value in scorer.items():
<scorer id="${key}">
${scorer2str(value)}</scorer>

    % endfor
% endif
% if header:
    % if prettify:
# DATA
    % endif
${tabjoin('ID', *header)}
% endif
