CREATE TABLE contactos (
    email varchar(100) PRIMARY KEY,
    nombre varchar(50),
    telefono varchar(12)
);

INSERT INTO contactos (email, nombre, telefono)
VALUES ("juan@example.com", "Juan Pérez", "555-123-4567");

INSERT INTO contactos (email, nombre, telefono)
VALUES ("maria@example.com", "María García", "555-678-9012");

CREATE TABLE usuarios (
    username varchar,
    password varchar,
    token varchar,
    timestamp timestamp
);

INSERT INTO usuarios (username, password, token, timestamp) 
VALUES ('brandon@mora.com', '202cb962ac59075b964b07152d234b70', '09b0ac835fe70eb1dc6d20d927af958d', CURRENT_TIMESTAMP);

INSERT INTO usuarios (username, password, token, timestamp) 
VALUES ('brandito@123.com', 'caf1a3dfb505ffed0d024130f58c5cfa', '09b0ac835fe70eb1dc6d20d927af958d', CURRENT_TIMESTAMP);INSERT INTO usuarios (username, password, token, timestamp) 
VALUES ('brandito@123.com', 'caf1a3dfb505ffed0d024130f58c5cfa', '09b0ac835fe70eb1dc6d20d927af958d', CURRENT_TIMESTAMP);