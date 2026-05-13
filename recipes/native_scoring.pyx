def jaccard_similarity(list base_ingredients, list candidate_ingredients):
    cdef int shared_count = 0
    cdef int total_count = 0
    cdef object ingredient

    base_set = set(base_ingredients)
    candidate_set = set(candidate_ingredients)

    for ingredient in base_set:
        if ingredient in candidate_set:
            shared_count += 1

    total_count = len(base_set | candidate_set)

    if total_count == 0:
        return 0.0

    return shared_count / total_count

    