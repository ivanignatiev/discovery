def flatten_json(input_json_object: dict | list) -> dict:
    out = {}

    def flatten(json_element, parent_json_key=''):
        if type(json_element) is dict:
            for json_element_key in json_element:
                flatten(json_element[json_element_key], parent_json_key + json_element_key + '_')
        elif type(json_element) is list:
            i = 0
            for json_list_element in json_element:
                flatten(json_list_element, parent_json_key + str(i) + '_')
                i += 1
        else:
            out[parent_json_key[:-1]] = json_element

    flatten(input_json_object)
    return out