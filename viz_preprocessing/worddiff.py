import re

epsilon = '&#949;'
pattern = r"(^|\s+)({0})($|\s+)"


default_span = {
    'archetype': 'archetype_part',
    'variation1': 'variation_part1',
    'variation2': 'variation_part2',
    'removed': 'removed_part',
    'added': 'added_part',
    'notclone': 'not_clone_part'
}


def replace_comment_stars(text):
    return re.sub(r'\n+\s*\*', '\n', text.replace('/**', '\n').replace('*/', ''))


def rindex(lst, value):
    for i, v in enumerate(reversed(lst)):
        if v == value:
            return len(lst) - i - 1  # return the index in the original list
    return None


def escape(text):
    import html
    return html.escape(text)


def split_text(text):
    """
    Splits text onto a tokens
    :param text:
    :return:
    """
    return re.split('\s+', re.sub('\s+', ' ', text).strip('  \n\t\r\0'))


def is_trash_between(beg, end, text):
    """
    Checks that fragment of text in text[beg:end] contains only trash
    :param beg:
    :param end:
    :param text:
    :return:
    """
    pattern_trash = r'(\/\*\*)|(\*\/)|(\n+\s*\*)|(\s+)'
    if re.fullmatch(pattern_trash, text[beg:end]) is not None:
        return True
    return False


def lcs(a, b):
    """

    :param a: list of elements
    :param b: list of elements
    :return: list of elements lcs of lists a and b
    """
    # find the length of the strings
    m = len(b)
    n = len(a)

    # declaring the array for storing the dp values
    dp = [[None] * (n + 1) for i in range(m + 1)]

    """Following steps build L[m + 1][n + 1] in bottom up fashion 
    Note: L[i][j] contains length of LCS of X[0..i-1] 
    and Y[0..j-1]"""
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                dp[i][j] = 0
            elif b[i - 1] == a[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    res = []

    while m > 0 and n > 0:

        if b[m - 1] == a[n - 1]:
            res.append(a[n - 1])
            m = m - 1
            n = n - 1
        else:
            if dp[m - 1][n] >= dp[m][n - 1]:
                m = m - 1
            else:
                n = n - 1
    res.reverse()
    return res


def get_with_variation(text1, text2):
    def get_index_arhcetype_tokens(tokens):
        """

        :param tokens:
        :param text:
        :return:
        """

        def is_mergable(beg1, end1, beg2, end2):
            if is_trash_between(beg1, end1, text1) and is_trash_between(beg2, end2, text2):
                return True
            else:
                return False

        ind_1 = [re.search(pattern.format(re.escape(tokens[0])), text1).regs[2]]
        ind_2 = [re.search(pattern.format(re.escape(tokens[0])), text2).regs[2]]
        offset1, offset2 = ind_1[-1][1], ind_2[-1][1]
        for i in range(1, len(tokens)):
            token = tokens[i]
            beg1, end1 = re.search(pattern.format(re.escape(token)), text1[offset1:]).regs[2]
            beg2, end2 = re.search(pattern.format(re.escape(token)), text2[offset2:]).regs[2]

            if is_mergable(ind_1[-1][1], beg1 + offset1, ind_2[-1][1], beg2 + offset2):
                ind_1[-1] = (ind_1[-1][0], end1 + offset1)
                ind_2[-1] = (ind_2[-1][0], end2 + offset2)
            else:
                ind_1.append((offset1 + beg1, offset1 + end1))
                ind_2.append((offset2 + beg2, offset2 + end2))
            offset1 += end1
            offset2 += end2

        if len(text1[offset1:str_end + 1]) > 0:
            ind_1[-1] = (ind_1[-1][0], ind_1[-1][1] + len(text1[offset1:str_end + 1]))
        if len(text2[offset2:str_end2 + 1]) > 0:
            ind_2[-1] = (ind_2[-1][0], ind_2[-1][1] + len(text2[offset2:str_end2 + 1]))
        return ind_1, ind_2

    def get_variation(arch_pos1, arch_pos2):
        # TODO if not trash then add /* till to not trash
        variation = []
        pos1_old, pos2_old = arch_pos1[0], arch_pos2[0]
        for (pos1, pos2) in zip(arch_pos1[1:], arch_pos2[1:]):
            if is_trash_between(pos1_old[1], pos1[0], text1):
                variation.append((epsilon, text2[pos2_old[1]:pos2[0]]))  # &#949;
            elif is_trash_between(pos2_old[1], pos2[0], text2):
                variation.append((text1[pos1_old[1]:pos1[0]], epsilon))
            else:
                variation.append((text1[pos1_old[1]:pos1[0]], text2[pos2_old[1]:pos2[0]]))
            #variation.append((text1[pos1_old[1]:pos1[0]], text2[pos2_old[1]:pos2[0]]))

            pos1_old = pos1
            pos2_old = pos2
        return variation

    tokenized_text1 = split_text(text1)
    tokenized_text2 = split_text(text2)
    archetype_tokens = lcs(tokenized_text1, tokenized_text2)

    if len(archetype_tokens) == 0:
        #TODO is that possible anyway?
        return None, None

    # token_beg, token_end = tokenized_text1.index(archetype_tokens[0]), rindex(tokenized_text1, archetype_tokens[-1])
    str_end = len(text1) - re.search(pattern.format(re.escape(archetype_tokens[-1][::-1])), text1[::-1]).regs[2][0]
    str_end2 = len(text2) - re.search(pattern.format(re.escape(archetype_tokens[-1][::-1])), text2[::-1]).regs[2][0]
    d = get_index_arhcetype_tokens(archetype_tokens)
    variation = get_variation(*d)
    return d, variation


def markup_with_diff_mode(text1, text2) -> [str]:
    """

    :param text1:
    :param text2:
    :return:
    """
    archetype_pos, variation = get_with_variation(text1, text2)
    if archetype_pos is None and variation is None:
        return ('<span class="{0}">'.format(default_span['variation1']) + '{0}</span>').format(escape(text1))

    pos_text1, pos_text2 = archetype_pos[0], archetype_pos[1]
    variation_text1 = [t for (t, _) in variation]

    templ_var1 = ('<span class="{0}">'.format(default_span['variation1']) + '{0}</span>')
    templ_arch = ('<span class="{0}">'.format(default_span['archetype']) + '{0}</span>')

    def pretitizer(text, arch1, var1):
        pretty_arch = [templ_arch.format(escape(text[beg:end])) for (beg, end) in arch1]
        pretty_var1 = [templ_var1.format(escape(v)) if epsilon not in v else
                       v.replace(epsilon, templ_var1.format(' '+ epsilon+' ')) for v in var1]
        pretty_clone = pretty_arch[0]
        pretty_clone += ''.join([b + a for (a, b) in zip(pretty_arch[1:], pretty_var1)])

        return templ_var1.format(escape(text1[:arch1[0][0]])) + pretty_clone + templ_var1.format(escape(text1[arch1[-1][1]:]))

    return pretitizer(text1, pos_text1, variation_text1)


#
# def get_difference(next_text, old_text):
#     """
#     :param next_text:
#     :param old_text:
#     :return:
#     """
#     import difflib
#     differ = difflib.Differ()
#
#     splitted_next, splitted_old = split_text(next_text), split_text(old_text)
#     arch = lcs(splitted_next, splitted_old)
#
#     if len(arch) == 0:
#         raise NotImplementedError
#
#     next_beg, next_end = splitted_next.index(arch[0]), rindex(splitted_next, arch[-1])
#
#     old_beg, old_end = splitted_old.index(arch[0]), rindex(splitted_old, arch[-1])
#
#     str_beg, str_end = re.search(r"(^|\s+)({0})($|\s+)".format(re.escape(arch[0])), next_text).regs[2][0], \
#                        len(next_text) - \
#                        re.search(r"(^|\s+)({0})($|\s+)".format(re.escape(arch[-1][::-1])), next_text[::-1]).regs[2][0]
#
#     immutable_start = '<span style="color:yellow">' + next_text[:str_beg] + '</span>'
#     immutable_end = '<span style="color:yellow">' + next_text[str_end + 1:] + '</span>'
#
#     def diffs_to_markup(text, diffs):
#         # TODO fix needs go for second textt
#         markup_text = ""
#         for diff in diffs:
#             if diff[0:2] in ['? ']:
#                 continue
#             if diff[0:2] in ['+ ']:
#                 markup_text += '<span style="color:red"> ' + diff[2:] + ' </span>'
#                 continue
#
#             beg, end = re.search(r"(^|\s+)({0})($|\s+)".format(re.escape(diff[2:])), text).regs[2]
#
#             if beg != 0:
#                 markup_text += text[:beg]
#             if diff[0:2] == '  ':
#                 # part of archetype
#                 markup_text += '<span style="color:gray">' + text[beg:end] + '</span>'
#             elif diff[0] == '?':
#                 ''
#             elif diff[0:2] == '- ':
#                 "added"
#                 markup_text += '<span style="color:green">' + text[beg:end] + '</span>'
#             elif diff[0:2] == '+ ':
#                 "dele"
#                 # markup_text = text[beg:end]
#             text = text[end:]
#
#         if len(text) > 0:
#             markup_text += text
#         return markup_text
#
#     diffs = list(differ.compare(splitted_next[next_beg:next_end + 1], splitted_old[old_beg:old_end + 1]))
#
#     return immutable_start + diffs_to_markup(next_text[str_beg:str_end + 1], diffs) + immutable_end

# TODo empty archetype
# def markup_with_variaton_mode(text1, text2) -> [str]:
#     """
#
#     :param text1:
#     :param text2:
#     :return:
#     """
#     archetype_pos, variation = get_with_variation(text1, text2)
#     # print( [text1[b:e] for (b,e) in archetype_pos[0]])
#     pos_text1, pos_text2 = archetype_pos[0], archetype_pos[1]
#     variation_text1 = [t for (t, _) in variation]
#     variation_text2 = [t for (_, t) in variation]
#
#     templ_var1 = ('<span class="{0}">'.format(default_span['variation1']) + '{0}</span>')
#     templ_var2 = ('<span class="{0}">'.format(default_span['variation2']) + '{0}</span>')
#     templ_arch = ('<span class="{0}">'.format(default_span['archetype']) + '{0}</span>')
#     templ_out = ('<span class="{0}">'.format(default_span['notclone']) + '{0}</span>')
#
#     def pretitizer(text, arch1, var1, var2, arch2):
#         pretty_arch = [templ_arch.format(escape(text[beg:end])) for (beg, end) in arch1]
#         pretty_var1 = [templ_var1.format(escape(v.rstrip(' \r\n\t'))) if epsilon not in v else v.replace(epsilon, templ_var1.format(' '+ epsilon)) for
#                        v in var1]
#         pretty_var2 = [templ_var2.format(escape(v.lstrip(' \r\n\t'))) if epsilon not in v else v.replace(epsilon, templ_var2.format(epsilon+ ' ')) for
#                        v in var2]
#         pretty_clone = pretty_arch[0]
#         pretty_clone += ''.join([b  + c  + a for (a, b, c) in zip(pretty_arch[1:], pretty_var1, pretty_var2)])
#
#         #TODO +1
#         return templ_var1.format(escape(text1[:arch1[0][0]].rstrip(' \r\n\t'))) + \
#                templ_var2.format(escape(text2[:arch2[0][0]].lstrip(' \r\n\t'))) + pretty_clone + \
#                templ_var1.format(escape(text1[arch1[-1][1]:].rstrip(' \r\n\t')))  + \
#                templ_var2.format(escape(text2[arch2[-1][1]:].lstrip(' \r\n\t')))
#
#     return pretitizer(text1, pos_text1, variation_text1, variation_text2, pos_text2)


