el1 = ['от', '\xa0', '60\xa0000\xa0руб.']
el2 = ['80\xa0000', '100\xa0000', '\xa0', 'руб.']
el3 = ['По договорённости']
el4 = ['до', '\xa0', '30\xa0000\xa0руб.']

def salary_format_sjru(el):
    def int_salary(st):
        return int(''.join([i for i in st if i in '0123456789']))

    min_salary, max_salary, currency = None, None, None

    #if el[0] == 'По договорённости':
    #    return min_salary, max_salary, currency

    if el[0] == 'от':
        min_salary = int_salary(el[2])
        currency = ''.join(i for i in el[2] if i.isalpha())

    elif el[0] == 'до':
        max_salary = int_salary(el[2])
        currency = ''.join(i for i in el[2] if i.isalpha())

    elif el[0][0].isdigit():
        min_salary = int_salary(el[0])
        max_salary = int_salary(el[1])
        currency = ''.join(i for i in el[3] if i.isalpha())

    return min_salary, max_salary, currency

print(salary_format_sjru(el1))
print(salary_format_sjru(el2))
print(salary_format_sjru(el3))
print(salary_format_sjru(el4))