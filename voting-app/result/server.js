const express = require('express');
const { Pool } = require('pg');
const path = require('path');

const app = express();
const port = 80;

// PostgreSQL connection
const pool = new Pool({
  host: 'db',
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD || 'postgres',
  database: process.env.POSTGRES_DB || 'postgres',
  port: 5432,
});

app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Wait for DB to be ready
async function waitForDB(retries = 10) {
  for (let i = 0; i < retries; i++) {
    try {
      await pool.query('SELECT 1');
      console.log('✅ Connected to PostgreSQL');
      return;
    } catch (err) {
      console.log(`⏳ Waiting for DB... attempt ${i + 1}/${retries}`);
      await new Promise(r => setTimeout(r, 2000));
    }
  }
  throw new Error('Could not connect to PostgreSQL');
}

// Results endpoint
app.get('/', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT vote, COUNT(id) AS count
      FROM votes
      GROUP BY vote
    `);

    const counts = { a: 0, b: 0 };
    result.rows.forEach(row => {
      counts[row.vote] = parseInt(row.count);
    });

    const total = counts.a + counts.b;
    const percentA = total > 0 ? Math.round((counts.a / total) * 100) : 50;
    const percentB = total > 0 ? Math.round((counts.b / total) * 100) : 50;

    res.render('index', {
      option_a: process.env.OPTION_A || 'Cats',
      option_b: process.env.OPTION_B || 'Dogs',
      count_a: counts.a,
      count_b: counts.b,
      percent_a: percentA,
      percent_b: percentB,
      total: total,
    });
  } catch (err) {
    console.error('Query error:', err);
    res.status(500).send('Error fetching results: ' + err.message);
  }
});

// Health check
app.get('/health', (req, res) => res.json({ status: 'ok' }));

waitForDB().then(() => {
  app.listen(port, () => {
    console.log(`📊 Result app running on port ${port}`);
  });
}).catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
