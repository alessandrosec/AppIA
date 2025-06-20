CREATE DATABASE BecasCiberseguridadDB;
GO

USE BecasCiberseguridadDB;
GO

CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL
);
GO

-- Opcional: Crear un índice para búsquedas rápidas por username
CREATE INDEX IX_Users_Username ON Users (username);
GO

CREATE TABLE Becarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    Nombres NVARCHAR(100) NOT NULL,
    Apellidos NVARCHAR(100) NOT NULL,
    Titulo NVARCHAR(100),
    FechaNacimiento DATE,
    CorreoPersonal NVARCHAR(100) UNIQUE, -- Un becario podría tener un correo personal y otro institucional
    CorreoInstitucional NVARCHAR(100) UNIQUE,
    Telefono NVARCHAR(20),
    Direccion NVARCHAR(255),
    PaisOrigen NVARCHAR(50),
    Nacionalidad NVARCHAR(50),
    HistorialCiberseguridad NVARCHAR(MAX), -- Para guardar historial como texto largo
    EsExIRSI BIT NOT NULL DEFAULT 0, -- 1 si ya pasó por IRSI, 0 si no
    FechaIngresoIRSI DATE -- Fecha en que ingresó al programa IRSI
);
GO

-- Índices para búsquedas rápidas, especialmente para el mecanismo antifraude
CREATE INDEX IX_Becarios_NombresApellidosFechaNacimiento
ON Becarios (Nombres, Apellidos, FechaNacimiento);

CREATE INDEX IX_Becarios_CorreoPersonal ON Becarios (CorreoPersonal);
CREATE INDEX IX_Becarios_CorreoInstitucional ON Becarios (CorreoInstitucional);
GO

CREATE TABLE AuditLogs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    timestamp DATETIME NOT NULL DEFAULT GETDATE(),
    user_id INT,
    username NVARCHAR(50),
    action_type NVARCHAR(50) NOT NULL, -- Ej: 'LOGIN', 'LOGOUT', 'CREATE_BECARIO', 'UPDATE_USER', 'DELETE_BECARIO', 'EXCEL_UPLOAD'
    description NVARCHAR(MAX),
    ip_address NVARCHAR(45), -- Para IPv4 e IPv6
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL
);
GO