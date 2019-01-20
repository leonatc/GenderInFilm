from data_loader import DataLoader
from imdb_matching import *

"""Statistics for matching."""

def _test_alignment_coverage(movie, alignment_fn):
    """
    Helper for test_alignment_coverage to count matches
    in an individual script.
    """
    inames = [c[0].lower() for c in movie.imdb_cast]
    chars_matched = 0
    chars_missed = 0
    lines_matched = 0
    lines_missed = 0

    for character in movie.characters:
        if any([alignment_fn(iname, character.name) for iname in inames]):
            chars_matched += 1
            lines_matched += len(character.line_data)
        else:
            chars_missed += 1
            lines_missed += len(character.line_data)

    return chars_matched, chars_missed, lines_matched, lines_missed

def test_all_alignment_coverage(data, alignment_fn):
    """
    Checks coverage for an alignment function.
    Provides two statistics:
    1. Characters covered - a script character is covered by
    alignment if it matches at least one IMDB name.
    2. Lines with alignments - a line is covered by alignment
    if it is spoken by a character with an aligned name.
    """
    total_chars_matched = 0
    total_lines_matched = 0
    total_chars_missed = 0
    total_lines_missed = 0
    for movie in data.movies:
        chars_matched, chars_missed, lines_matched, lines_missed = (
                    _test_alignment_coverage(movie, alignment_fn))
        total_chars_matched += chars_matched
        total_chars_missed += chars_missed
        total_lines_matched += lines_matched
        total_lines_missed += lines_missed

    total_chars = total_chars_matched + total_chars_missed
    total_lines = total_lines_matched + total_lines_missed

    print('ALIGNMENT TEST: %s' % (alignment_fn.__name__))
    print('Total Characters Covered: {} / {}% \
    Total Characters Missed: {} / {}%' .format(total_chars_matched,
                                              round(total_chars_matched/total_chars * 100, 2),
                                              total_chars_missed,
                                              round(total_chars_missed/total_chars * 100, 2)))
    print('Total Lines Covered: {} / {}% \
    Total Lines Missed: {} / {}%' .format(total_lines_matched,
                                          round(total_lines_matched/total_lines * 100, 2),
                                          total_lines_missed,
                                          round(total_lines_missed/total_lines * 100, 2)))
    print('----------------------------')

def _test_assignment_coverage(movie, alignment_fn, assignment_fn):
    """
    Helper for test_all_assignment_coverage to count matches
    in an individual script.
    """
    success = 0
    failure = 0
    chars_matched = 0
    chars_missed = 0
    lines_matched = 0
    lines_missed = 0
    chars_gendered = 0

    inames = get_imdb_gender_mapping(movie.imdb_cast)
    script_to_imdb = defaultdict(list)
    aligned_char_count = 0
    aligned_line_count = 0
    # Align script characters to possible IMDb characters.
    for character in movie.characters:
        for iname in inames:
            if alignment_fn(iname, character.name):
                script_to_imdb[character.name].append(iname)
        if character.name not in script_to_imdb.keys():
            chars_missed += 1 # Record lines and character as unmatched.
            lines_missed += len(character.line_data)
        else:
            aligned_line_count += len(character.line_data) # Store for later processing.
            aligned_char_count += 1

    # Check final assignments and calculate final numbers.
    assignment = assignment_fn(script_to_imdb)
    if assignment:
        for sname in assignment:
            gender = inames[assignment[sname]]
            if gender == 'M' or gender == 'F':
                chars_gendered += 1
        success += 1
        chars_matched += aligned_char_count
        lines_matched += aligned_line_count

    else:
        failure += 1
        chars_missed += aligned_char_count
        lines_missed += aligned_line_count

    return success, failure, chars_matched, chars_missed, \
           lines_matched, lines_missed, chars_gendered

def test_all_assignment_coverage(data, alignment_fn, assignment_fn):
    """
    Tests coverage of assignments from alignments.
    Provides four statistics:
    1. Files with successful assignment - a file produces
    some assignment of names to IMDb characters. Failure
    happens if all possible assignments are inconsistent
    (according to the assignment criteria being used in the
    assignment_fn), or if there is no IMDB data to align.
    2. Number of characters successfully assigned - characters
    with an IMDb match.
    3. Number of lines successfully assigned - lines spoken
    by characters with an IMDB match.
    4. Number of characters successfully gendered -  characters
    with an IMDb match that has a gender.
    """
    total_success = 0
    total_failure = 0
    total_chars_matched = 0
    total_chars_missed = 0
    total_lines_matched = 0
    total_lines_missed = 0
    total_chars_gendered = 0

    for movie in data.movies:
        success, failure, chars_matched, chars_missed, lines_matched, lines_missed, chars_gendered = (
                    _test_assignment_coverage(movie, alignment_fn, assignment_fn))
        total_success += success
        total_failure += failure
        total_chars_matched += chars_matched
        total_chars_missed += chars_missed
        total_lines_matched += lines_matched
        total_lines_missed += lines_missed
        total_chars_gendered += chars_gendered

    total_attempts = total_success + total_failure
    total_chars = total_chars_matched + total_chars_missed
    total_lines = total_lines_matched + total_lines_missed

    print('ASSIGNMENT TEST: %s assignment with %s alignment' % (assignment_fn.__name__, alignment_fn.__name__))
    print('File assignment successes: {} / {}%  \
           File assignment failures: {} / {}%'.format(total_success,
                                                      round(total_success/total_attempts * 100, 2),
                                                      total_failure,
                                                      round(total_failure/total_attempts * 100, 2)))
    print('Characters matched: {} / {}%  \
           Characters missed: {} / {}%'.format(total_chars_matched,
                                               round(total_chars_matched/total_chars * 100, 2),
                                               total_chars_missed,
                                               round(total_chars_missed/total_chars * 100, 2)))

    print('Lines matched: {} / {}%  \
           Lines missed: {} / {}%'.format(total_lines_matched,
                                          round(total_lines_matched/total_lines * 100, 2),
                                          total_chars_missed,
                                          round(total_lines_missed/total_lines * 100,2)))

    print('Characters gendered: {} / {}%  \
           Characters not gendered: {} / {}%'.format(total_chars_gendered,
                                                     round(total_chars_gendered/total_chars * 100, 2),
                                                     total_chars - total_chars_gendered,
                                                     round((total_chars - total_chars_gendered)/total_chars * 100, 2)))

    print('----------------------------')

if __name__ == "__main__":
    data = DataLoader()
    test_all_alignment_coverage(data, in_align)
    test_all_alignment_coverage(data, threshold_align)
    test_all_alignment_coverage(data, blended_align)
    test_all_assignment_coverage(data, in_align, soft_backtrack)
    test_all_assignment_coverage(data, threshold_align, soft_backtrack)
    test_all_assignment_coverage(data, blended_align, soft_backtrack)
    test_all_assignment_coverage(data, in_align, hard_backtrack)
    test_all_assignment_coverage(data, threshold_align, hard_backtrack)
    test_all_assignment_coverage(data, blended_align, hard_backtrack)