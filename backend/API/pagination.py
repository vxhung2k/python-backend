from django.http import JsonResponse
import math


def CheckTypeItems(items, start, end):
    if type(items) is list:
        return items[start:end]
    else:
        return items[slice(start, end)]


def Pagination(items, page, limit_page):
    total = len(items)
    total_page = math.ceil(total / limit_page)
    list_items = {'limit': limit_page, 'total': total, 'page': page, 'totalPage': total_page}
    if total == 0:
        return JsonResponse({'message': 'no data !'}, status=404)
    elif total < limit_page:
        has_next_page = False
        has_prev_page = False
        list_items.update({'items': items, 'hasNextPage': has_next_page, 'hasPrevPage': has_prev_page})
        return list_items
    else:
        if page == 1:
            serializer = CheckTypeItems(items, 0, limit_page)
            has_next_page = True
            has_prev_page = False
            list_items.update({'items': serializer, 'hasNextPage': has_next_page, 'hasPrevPage': has_prev_page})
            return list_items

        elif page == total_page:
            # serializer = items[slice(page * limit_page - 1, total)]
            serializer = CheckTypeItems(items, page * limit_page - 1, total)
            has_next_page = False
            has_prev_page = True
            list_items.update({'items': serializer, 'hasNextPage': has_next_page, 'hasPrevPage': has_prev_page})
            return list_items
        else:
            # serializer = items[slice((page - 1) * limit_page, page * limit_page)]
            serializer = CheckTypeItems(items, (page - 1) * limit_page, page * limit_page)
            has_next_page = True
            has_prev_page = True
            list_items.update({'items': serializer, 'hasNextPage': has_next_page, 'hasPrevPage': has_prev_page})
            return list_items
