<%
    concept2id = {obj.concepts[i]: i + 1 for i in range(len(obj.concepts))}
    this_idx = lambda cogid: [x for x in obj.etd[ref][cogid] if x != 0][0][0]
%>\
${obj.filename}
% for concept in obj.concepts:

    % for cogid in get_cogids(concept):
        % if cogid in obj.msa[ref]:
            % for i, alm in enumerate(obj.msa[ref][cogid]['alignment']):
${util.tabjoin(obj[obj.msa[ref][cogid]['ID'][i], ref], obj.msa[ref][cogid]['taxa'][i], concept, concept2id[concept], get_alm_string(i, cogid))}
            % endfor
        % else:
${util.tabjoin(cogid, obj[this_idx(cogid), 'taxon'], concept, concept2id[concept], ''.join(obj[this_idx(cogid), 'ipa'] or ' '.join(obj[this_idx(cogid), 'tokens'])))}
        % endif
    % endfor
% endfor