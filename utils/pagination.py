def paginate_data(data_list, begin, count):
    start_idx = (begin - 1) if begin > 0 else 0
    end_idx = start_idx + count
    return data_list[start_idx:end_idx], len(data_list) 