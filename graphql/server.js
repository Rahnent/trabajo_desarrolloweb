const express = require('express');
const { ApolloServer, gql } = require('apollo-server-express');
const mongoose = require('mongoose');
const cors = require('cors');
const Usuario = require('./models/usuario');

mongoose.connect('mongodb://127.0.0.1:27017/clase_graphql')
    .then(() => console.log('Conectado a MongoDB'))
    .catch(err => console.error('Error al conectar MongoDB:', err));

const typeDefs = gql`
    type Usuario {
        id: ID!
        nombre: String!
        pass: String!
    }

    input UsuarioInput {
        nombre: String!
        pass: String!
    }

    type Alert {
        message: String
    }

    type Query {
        getUsuarios: [Usuario]
        getUsuariosById(id: ID!): Usuario
    }

    type Mutation {
        addUsuario(input: UsuarioInput): Usuario
        updUsuario(id: ID!, input: UsuarioInput): Usuario
        delUsuario(id: ID!): Alert
    }
`;

const resolvers = {
    Query: {
        async getUsuarios() {
            return await Usuario.find();
        },
        async getUsuariosById(obj, { id }) {
            const usuarioBus = await Usuario.findById(id);
            if (usuarioBus == null) {
                return null;
            }
            return usuarioBus;
        }
    },
    Mutation: {
        async addUsuario(obj, { input }) {
            const nuevoUsuario = new Usuario(input);
            return await nuevoUsuario.save();
        },
        async updUsuario(obj, { id, input }) {
            return await Usuario.findByIdAndUpdate(id, input, { new: true });
        },
        async delUsuario(obj, { id }) {
            await Usuario.findByIdAndDelete(id);
            return { message: "Usuario eliminado correctamente" };
        }
    }
};

async function startServer() {
    const app = express();
    app.use(cors());

    const server = new ApolloServer({
        typeDefs,
        resolvers
    });

    await server.start();
    server.applyMiddleware({ app });

    const PORT = 4000;
    app.listen(PORT, () => {
        console.log('Graphql Iniciado');
        console.log(`Servidor listo en http://localhost:${PORT}${server.graphqlPath}`);
    });
}

startServer();