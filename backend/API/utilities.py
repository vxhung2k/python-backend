import re


def password_check(passwd):
    uuid_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,20}$', re.IGNORECASE)
    if uuid_pattern.match(passwd):
        return True
    else:
        return False


def checkUUID(val):
    uuid_pattern = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    if uuid_pattern.match(val):
        return True
    else:
        return False


def Price(options, models):
    price = 0
    for x in options.all():
        price = models.objects.get(id=x.id).price
        break
    return price


def SearchRangePrice(data_search, range_value, models_serializer, models):
    list_res = []
    range_value_arg = range_value.split('-')
    from_value = range_value_arg[0]
    to_value = range_value_arg[1]
    if from_value and not to_value:
        for i in data_search:
            if Price(i.options, models) > float(from_value):
                item = models_serializer(i)
                list_res.append(item.data)
        return list_res
    elif to_value and not from_value:
        for i in data_search:
            if Price(i.options, models) < float(to_value):
                item = models_serializer(i)
                list_res.append(item.data)
            return list_res
    else:
        for i in data_search:
            if float(to_value) > Price(i.options, models) > float(from_value):
                item = models_serializer(i)
                list_res.append(item.data)
        return list_res


def CheckLevelCustomer(price):
    if price < 1000000:
        return 'bronze'
    elif 1000000 <= price < 3000000:
        return 'silver'
    elif 3000000 <= price < 10000000:
        return 'gold'
    else:
        return 'diamond'

