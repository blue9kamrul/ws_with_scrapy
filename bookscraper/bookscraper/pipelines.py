# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        # Here you can process the item, e.g., clean data, validate fields, etc.
        # For example, you can convert the price to a float if it's a string:
        #here striping the whitespace from the fields
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            adapter[field_name] = value[0].strip()

        #category & product type are being switched to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        
        #price data as float type
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        #availability is being converted to integer
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])
            #in stock (18 available)
            #so it first splits with "(" and then if < 2 then 0 
            #otherwise it slects 18

        #review number converted from string to integer
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)


        #star ratinf to integer
        stars_rating = adapter.get('stars')
        split_string_array = stars_rating.split(' ')
        stars_text_value = split_string_array[1].lower()
        if stars_text_value == 'zero':
            adapter['stars'] = 0
        elif stars_text_value == 'one':
            adapter['stars'] = 1   
        elif stars_text_value == 'two':
            adapter['stars'] = 2
        elif stars_text_value == 'three':   
            adapter['stars'] = 3
        elif stars_text_value == 'four':
            adapter['stars'] = 4
        elif stars_text_value == 'five':    
            adapter['stars'] = 5

        return item

#make sure at settings.py the pipeline is enabled