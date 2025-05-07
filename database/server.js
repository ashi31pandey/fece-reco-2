const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(cors());

const db = mysql.createConnection({
    host: 'localhost',
    port: 3306,
    user: 'root',       // Your MySQL username
    password: '3112',   // Your MySQL password
    database: 'user-auth'
});

db.connect((err) => {
    if (err) {
        console.error('Error connecting to the database:', err);
        return;
    }
    console.log('Connected to the database');
});

app.post('/register', async (req, res) => {
    const { firstname, lastname, email, password } = req.body;
    
    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    const query = 'INSERT INTO users (firstname, lastname, email, password) VALUES (?, ?, ?, ?)';
    db.query(query, [firstname, lastname, email, hashedPassword], (err, result) => {
        if (err) {
            console.error('Error inserting user:', err);
            res.status(500).send('Registration failed');
            return;
        }
        res.status(201).send('User registered successfully');
    });
});

app.post('/login', (req, res) => {
    const { email, password } = req.body;

    const query = 'SELECT * FROM users WHERE email = ?';
    db.query(query, [email], async (err, results) => {
        if (err) {
            console.error('Error fetching user:', err);
            res.status(500).send('Login failed');
            return;
        }

        if (results.length === 0) {
            res.status(400).send('Invalid email or password');
            return;
        }

        const user = results[0];

        // Compare the password
        const isMatch = await bcrypt.compare(password, user.password);

        if (!isMatch) {
            res.status(400).send('Invalid email or password');
            return;
        }

        // Generate a JWT token
        const token = jwt.sign({ id: user.id, email: user.email }, 'your_jwt_secret', {
            expiresIn: '1h'
        });

        res.status(200).send({ message: 'Login successful', token });
    });
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
