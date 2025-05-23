# Dockerfile
FROM node:18-alpine

# Install essential build tools and Git
RUN apk add --no-cache git python3 make g++

# Set working directory
WORKDIR /usr/src/app

# Install JS dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app
COPY . .

# Expose Metro bundler port
EXPOSE 8081

# Start Metro by default
CMD ["npm", "start"]
