from __future__ import annotations

from typing import Any
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring


class XMLExporter:
    def export(self, root: Any) -> str:
        element = self._node_to_xml(root)
        rough = tostring(element, encoding="utf-8")
        return minidom.parseString(rough).toprettyxml(indent="  ")

    def _node_to_xml(self, node: Any) -> Element:
        element = Element(node.kind.lower())
        if node.name:
            element.set("nombre", node.name)
        if node.attributes:
            attrs = SubElement(element, "atributos")
            for key, value in node.attributes.items():
                attr = SubElement(attrs, key.lower())
                attr.text = self._format_value(value)
        for child in node.children:
            element.append(self._node_to_xml(child))
        return element

    def _format_value(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(str(item) for item in value.values() if item is not None)
        if isinstance(value, list):
            return ", ".join(self._format_value(item) for item in value)
        return str(value)
