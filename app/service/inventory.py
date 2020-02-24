def get_insert_request_data(request):
    # Validate required request data is available or not
    if "File" in request.files and "name" in request.form and "category" in request.form and "quantity" in request.form:
        request_data = {}
        file = request.files['File']
        request_data['name'] = request.form.get('name')
        request_data['category'] = request.form.get('category')
        request_data['quantity'] = request.form.get('quantity')
        return True, request_data, file
    return False, None, None


def get_search_request_data(request):
    # Validate required request data is available or not
    name = request.args.get('name')
    category = request.args.get('category')
    if name or category:
        return True, name, category
    return False, None, None
