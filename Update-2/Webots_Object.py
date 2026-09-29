class ObjectManager:

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.objects = {}
        self.next_id = 0

    def createObject(self, position, size, color):

        x, y, z = position
        sx, sy, sz = size
        r, g, b = color

        object_id = f"object_{self.next_id}"
        self.next_id += 1

        children = self.supervisor.getRoot().getField("children")

        node_string = f"""
        Transform {{
            translation {x} {y} {z}
            children [
                Shape {{
                    appearance PBRAppearance {{
                        baseColor {r} {g} {b}
                    }}
                    geometry Box {{
                        size {sx} {sy} {sz}
                    }}
                }}
            ]
        }}
        """

        children.importMFNodeFromString(-1, node_string)

        node = children.getMFNode(-1)

        self.objects[object_id] = node

        return object_id

    def deleteObject(self, object_id):

        if object_id in self.objects:
            self.objects[object_id].remove()
            del self.objects[object_id]
            return True

        return False