const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3030;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const dataDir = path.join(__dirname, 'data');

const reviewsData = JSON.parse(
  fs.readFileSync(path.join(dataDir, 'reviews.json'), 'utf8')
);
const dealershipsData = JSON.parse(
  fs.readFileSync(path.join(dataDir, 'dealerships.json'), 'utf8')
);
const carsData = JSON.parse(
  fs.readFileSync(path.join(dataDir, 'car_records.json'), 'utf8')
);

const Reviews = require('./review');
const Dealerships = require('./dealership');
const Cars = require('./inventory');

const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017/dealershipsDB';

async function startServer() {
  try {
    await mongoose.connect(mongoUrl);
    console.log('Connected to MongoDB');

    await Reviews.deleteMany({});
    await Dealerships.deleteMany({});
    await Cars.deleteMany({});

    await Reviews.insertMany(reviewsData.reviews);
    await Dealerships.insertMany(dealershipsData.dealerships);
    await Cars.insertMany(carsData.cars);

    console.log('Dealership, review and car data loaded');

    app.get('/', (req, res) => {
      res.send('Welcome to the Cars Dealership API');
    });

    app.get('/fetchReviews', async (req, res) => {
      try {
        res.json(await Reviews.find());
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    app.get('/fetchReviews/dealer/:id', async (req, res) => {
      try {
        res.json(await Reviews.find({
          dealership: Number(req.params.id)
        }));
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    app.get('/fetchDealers', async (req, res) => {
      try {
        res.json(await Dealerships.find().sort({ id: 1 }));
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    app.get('/fetchDealers/:state', async (req, res) => {
      try {
        const state = req.params.state;

        const dealers = state.toLowerCase() === 'all'
          ? await Dealerships.find().sort({ id: 1 })
          : await Dealerships.find({
              $or: [
                { state: new RegExp(`^${state}$`, 'i') },
                { st: new RegExp(`^${state}$`, 'i') }
              ]
            }).sort({ id: 1 });

        res.json(dealers);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    app.get('/fetchDealer/:id', async (req, res) => {
      try {
        const dealer = await Dealerships.findOne({
          id: Number(req.params.id)
        });

        if (!dealer) {
          return res.status(404).json({ error: 'Dealer not found' });
        }

        res.json(dealer);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    app.get('/fetchCars', async (req, res) => {
      try {
        const cars = await Cars.find();
        const uniqueCars = [...new Map(
          cars.map(car => [
            `${car.make}-${car.model}`,
            {
              CarMake: car.make,
              CarModel: car.model
            }
          ])
        ).values()];

        res.json({ CarModels: uniqueCars });
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    app.post('/insert_review', async (req, res) => {
      try {
        const data = req.body;

        const latest = await Reviews.findOne().sort({ id: -1 });
        const newId = latest ? latest.id + 1 : 1;

        const review = await Reviews.create({
          id: newId,
          name: data.name,
          dealership: Number(data.dealership),
          review: data.review,
          purchase: data.purchase !== false,
          purchase_date: data.purchase_date,
          car_make: data.car_make,
          car_model: data.car_model,
          car_year: Number(data.car_year)
        });

        res.status(201).json(review);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    app.listen(port, '0.0.0.0', () => {
      console.log(`Server is running on port ${port}`);
    });

  } catch (error) {
    console.error('Database startup failed:', error);
    process.exit(1);
  }
}

startServer();
