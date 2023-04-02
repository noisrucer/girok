import girok.server.src.category.constants as category_constants


class CategoryAlreadyExistsException(Exception):
    def __init__(self, sup, sub):
        if sup == "":
            self.detail = f"There already exists a category named '{sub}'."
        else:
            self.detail = f"'{sup}' already has a subcategory named '{sub}'"
        

class CategoryNotExistException(Exception):
    def __init__(self, name):
        self.detail = f"Category '{name}' does not exist."
        
        
class SubcategoryNotExistException(Exception):
    def __init__(self, sup, sub):
        if sup == "":
            self.detail = f"There is no category named {sub}."
        else:
            self.detail = f"'{sup}' does not have a subcategory named '{sub}'"
            

class CannotMoveRootDirectoryException(Exception):
    def __init__(self):
        self.detail = "Cannot move the root directory!"
        
        
class CannotMoveToSameLocation(Exception):
    def __init__(self):
        self.detail = "[Warning] Circular reference prohibited."
        
        
class CategoryColorException(Exception):
    def __init__(self, cat_path, color, parent_cat_path, parent_color):
        self.detail = f"You have given {color} color for {cat_path}. However, {parent_cat_path} already has a color {parent_color}"
        
class CategoryColorNotExistException(Exception):
    def __init__(self, color):
        self.detail = f"'{color}' is not a valid color. Please choose from {category_constants.CATEGORY_COLORS}."