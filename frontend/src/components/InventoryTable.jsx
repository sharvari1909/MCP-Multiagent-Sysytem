export default function InventoryTable({ inventory }) {
  return (
    <div className="panel">
      <h3>Demo Odoo-like Inventory</h3>

      <table className="inventory-table">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Product</th>
            <th>Stock</th>
            <th>Price</th>
          </tr>
        </thead>

        <tbody>
          {inventory.map((item) => (
            <tr key={item.sku}>
              <td>{item.sku}</td>
              <td>{item.name}</td>
              <td>{item.stock}</td>
              <td>₹{item.price}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}