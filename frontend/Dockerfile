# Use the Node.js base image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Update npm to the latest version
RUN npm install -g npm@10.9.2

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install --force

# Copy the source code
COPY . .

# Build the application
RUN npm run build

# Expose the port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
