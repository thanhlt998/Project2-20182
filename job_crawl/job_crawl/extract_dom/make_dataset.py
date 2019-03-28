from lxml import etree


class DatasetFromHTML:
    def __int__(self, selectors, type_selector='xpath'):
        self.selectors = selectors
        self.type_selector = type_selector


    def clean_dom(self, dom):
        remove_tags = ['script', 'style', 'br', 'head']
        for node in dom.iter():
            if node.tag in remove_tags:
                node.getparent().remove(node)


    def get_data_from_html(self, html):
        # Replace <br> by </br>
        html = html.replace('<br>', '</br>')
