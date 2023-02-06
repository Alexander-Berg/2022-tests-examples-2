# coding: utf-8

from enum import Enum


class Graph:
    class VertexColor(Enum):
        white = 'WHITE'
        grey = 'GREY'
        red = 'RED'
        green = 'GREEN'

    class Vertex:
        def __init__(self, name, neighbours, depends, task_ids=None, color='white', allow_failure=False):
            self.name = name
            self.neighbours = neighbours
            self.depends = depends
            self.color = Graph.VertexColor[color]
            self.task_ids = task_ids
            self.allow_failure = allow_failure

        def serialize(self):
            res = self.__dict__.copy()
            res.update(color=self.color.name, allow_failure=self.allow_failure)
            return res

    def __init__(self, vertices=None):
        if vertices is None:
            self.vertices = dict()
        else:
            self.vertices = self._get_graph_from_dict(vertices)

    def add_vertex(self, name, neighbours, allow_failure=False):
        """Добавить вершину в граф"""
        depends = list()
        for vertex_name, vertex in self.vertices.items():
            if name in vertex.neighbours:
                depends.append(vertex_name)
        vertex = Graph.Vertex(name, neighbours, depends, allow_failure=allow_failure)
        self.vertices[name] = vertex

    def get_vertex(self, vertex_name):
        return self.vertices[vertex_name]

    def get_vertices(self):
        return self.vertices.keys()

    def prune(self, root_vertex):
        """Выделить минимальный подграф (по кол-ву вершин) содержащий в себе данную вершину и все ее зависимости"""
        if root_vertex not in self.vertices:
            return

        visited = set()
        active_vertices = set()

        def traverse_graph(vertex):
            """
            vertex: string  vertex ID
            """
            visited.add(vertex)
            active_vertices.add(vertex)
            for u in self.vertices[vertex].depends:
                if not visited.get(u):
                    traverse_graph(u)

        traverse_graph(root_vertex)
        excluded_vertices = list(set(self.vertices.keys()) - active_vertices)
        for deleted_vertex in excluded_vertices:
            self.vertices.pop(deleted_vertex)
            for vertex in self.vertices.values():
                if deleted_vertex in vertex.neighbours:
                    vertex.neighbours.remove(deleted_vertex)
                if deleted_vertex in vertex.depends:
                    vertex.depends.remove(deleted_vertex)

    def serialize(self):
        """Сериализация графа в словарь (для последующего сохранения в Context)"""
        res = dict()
        for vertex_name, vertex in self.vertices.items():
            res[vertex_name] = vertex.serialize()
        return res

    def top_sort(self, root):
        """Выполняет топологическую сортировку графа и на выход выдает массив вершин"""
        queue = list()
        visited = dict()

        def dfs(v):
            visited[v] = True
            for u in self.get_vertex(v).neighbours:
                if not visited.get(u):
                    dfs(u)
            queue.append(v)
        dfs(root)
        queue.reverse()
        return queue

    def _get_graph_from_dict(self, vertices):
        res = dict()
        for vertex_name, vertex_info in vertices.items():
            vertex = Graph.Vertex(
                name=vertex_name,
                neighbours=vertex_info['neighbours'],
                depends=vertex_info['depends'],
                task_ids=vertex_info['task_ids'],
                color=vertex_info['color'],
                allow_failure=vertex_info['allow_failure'],
            )
            res[vertex_name] = vertex
        return res
