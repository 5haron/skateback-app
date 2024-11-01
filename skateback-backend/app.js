const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

app.post('/accelerate', (req, res) => {
  console.log("Accelerating");
  res.send({ message: 'Accelerating' });
});

app.post('/decelerate', (req, res) => {
  console.log("Decelerating");
  res.send({ message: 'Decelerating' });
});

app.post('/reverse', (req, res) => {
  console.log("Reversing");
  res.send({ message: 'Reversing' });
});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
