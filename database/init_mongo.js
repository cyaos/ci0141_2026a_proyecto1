db = db.getSiblingDB("distributed_client_db");

db.estudiantes.insertMany([
  {
    carne: "C23913",
    nombre: "Elizabeth Huang",
    nota_actual: 88.00
  },
  {
    carne: "C67890",
    nombre: "Luis Mora",
    nota_actual: 75.50
  },
  {
    carne: "A11111",
    nombre: "María Solano",
    nota_actual: 91.25
  }
]);