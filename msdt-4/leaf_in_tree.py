import sys
import os


class Node:
    """Класс, представляющий узел дерева."""

    def __init__(self, value):
        """Инициализация узла"""

        self.value = value
        self.children = []


    def add_child(self, child_node):
        """Добавление дочернего узла"""

        self.children.append(child_node)


class Tree:
    """Класс, представляющий узел дерева."""

    def __init__(self, root = None):
        """Инициализация дерева"""

        self.root = root
        self.nodes = {}
    
    
    def get_node(self, value):
        """Получение узла по значению"""

        if value in self.nodes:
            return self.nodes[value]
        else:
            return None
    
    
    def get_parent(self, value):
        """Получение списка родителей узла"""

        res = []
        for node in self.nodes.values():
            if value in node.children:
                res.append(node)
        return res
        

    def visualization(self):
        """Отображение всех узлов"""

        for i in self.nodes.keys():
            print(f'Узел: {i}. Дети: {[str(j.value) + " " for j in self.nodes[i].children]}')


    def get_count_leafs(self):
        """Подсчет листьев"""

        res = 0
        for node in self.nodes.values():
            if node.children == []:
                res += 1
        return res


def parsing(f):
    """Парсинг файла"""

    tree = Tree()

    for line_num, line in enumerate(f, 1):
    
        if ':' not in line:
            raise ValueError("Строка не содержит символ ':'")
        
        if ' ' in line:
            raise ValueError("Строка содержит пробелы")
        
        st = line.strip().split(':')
        head = st[0]
        tail = st[1].split(',')

        if not head:
            raise ValueError("Пустое имя узла перед символом ':'")

        if tree.get_node(head) is None:
            new_node = Node(head)
            tree.nodes[head] = new_node
    
        else:
            new_node = tree.get_node(head)
        
        
        if tail[0] != '':
            for i in tail:
                if tree.get_node(i) == None:
                    child_node = Node(i)
                    tree.nodes[i] = child_node
                else:
                    child_node = tree.get_node(i)

                new_node.add_child(child_node)

        if len(new_node.children) != len(set(new_node.children)):
            raise ValueError("Присутствие узлов с неуникальными названиями")
    
    #После парсинга определяется корень дерева
    for node in tree.nodes.values():
        parents = tree.get_parent(node)

        if len(parents) > 1:
            raise ValueError("Присутствие узлов с двумя или более родителями")

        elif len(parents) == 0 and tree.root == None:
            tree.root = node

        elif len(parents) == 0 and tree.root != None:
            raise ValueError("Присутствие более одного корневого узла")
        
    if tree.root == None:
        raise ValueError("Отсутствие корневого узла")
    return tree


def run(file_name):
    """Запуск обработки файла"""

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            new_tree = parsing(file)
            leaf_count = new_tree.get_count_leafs()
            print(f'Количество листьев в данном дереве: {leaf_count}')
            return leaf_count
        
    except FileNotFoundError:
        print(f"Файл {file_name} не найден")
        raise

    except ValueError as e:
        print(f"Ошибка в формате данных: {e}", file=sys.stderr)
        raise

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        print(f'Используется: python leaf_in_tree.py {file_name}')
        try:
            run(file_name)
        except (ValueError, FileNotFoundError) as e:
            sys.exit(1)
    else:
        print("Укажите имя файла: python leaf_in_tree.py <filename>", file=sys.stderr)
        sys.exit(1)
