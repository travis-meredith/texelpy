
from __future__ import annotations

from _collections_abc import dict_items
from blocks.blockprotocol import ItemProtocol

from .inventoryprotocol import InventoryProtocol


class Inventory(InventoryProtocol):
    """
    dict based inventory. Unlimited size, automatically stacks items.
    """

    inventory: dict[ItemProtocol, int]

    def __init__(self):
        self.inventory = {}

    def __iter__(self) -> dict_items[ItemProtocol, int]:
        return self.inventory.items()

    def add(self, item: ItemProtocol, quantity: int=1):
        """Add item to inventory with quantity
        Note: this is for spawning new items in
        *not* for transfering items between inventories; use
        try_transfer for that
        """
        self.inventory[item] = self.inventory.get(item, 0) + quantity

    def remove(self, item: ItemProtocol, quantity: int=1):
        """Remove quantity of item from inventory"""
        self.inventory[item] = self.inventory.get(item, 0) - quantity
        if self.inventory[item] < 1:
            del self.inventory[item]
    
    def transfer(self, /, *, item: ItemProtocol, inventory: InventoryProtocol, quantity: int=1):
        """move item from this Inventory to another InventoryProtocol
        raises ValueError on failure"""
        if self.try_transfer(
                item=item, 
                inventory=inventory, 
                quantity=quantity):
            return
        raise ValueError(f"Could not transfer {item} from {self} to {inventory} in amount {quantity}")

    def try_transfer(self, /, *, item: ItemProtocol, inventory: InventoryProtocol, quantity: int = 1) -> bool:
        """move item from this Inventory to another InventoryProtocol
        return success flag"""
        if self.has_item(item, quantity) and inventory.has_space(quantity):
            self.remove(item, quantity)
            inventory.add(item, quantity)
            return True
        return False

    def has_item(self, item: ItemProtocol, quantity: int=1) -> bool:
        return (self.inventory.get(item, 0) - quantity) >= 0

    def has_space(self, amount: int=1):
        return True

    def as_list(self) -> list[tuple[ItemProtocol, int]]:
        return list(self.inventory.items())

    def as_dict(self) -> dict[ItemProtocol, int]:
        return {item: quantity for item, quantity in self.inventory.items()}

class Tools(InventoryProtocol):

    inventory: list[ItemProtocol]

    def __init__(self):
        self.inventory = []

    def __iter__(self):
        return [(item, 1) for item in self.inventory]

    def add(self, item: ItemProtocol, quantity: int=1):
        self.inventory.append(item)

    def remove(self, item: ItemProtocol, quantity: int=1):
        self.inventory.remove(item)

    def transfer(self, /, *, item: ItemProtocol, inventory: InventoryProtocol, quantity: int=1):
        if self.try_transfer(
                item=item,
                inventory=inventory,
                quantity=quantity
                ):
            return
        raise ValueError(f"Could not transfer {item} from tools {self} to {inventory} in amount {quantity}")

    def try_transfer(self, /, *, item: ItemProtocol, inventory: InventoryProtocol, quantity: int=1) -> bool:
        if quantity != 1:
            raise ValueError("Cannot assign quantity to tools belt transfer")
        if self.has_item(item) and inventory.has_space(1):
            self.remove(item)
            inventory.add(item, 1)
            return True
        return False

    def has_item(self, item: ItemProtocol, quantity: int=1) -> bool:
        return item in self.inventory

    def has_space(self, amount: int=1):
        return True

    def as_list(self) -> list[tuple[ItemProtocol, int]]:
        return [(item, 1) for item in self.inventory]

    def as_dict(self) -> dict[ItemProtocol, int]:
        return {item: 1 for item in self.inventory}
    
    def as_flat_list(self) -> list[ItemProtocol]:
        return [item for item in self.inventory]
