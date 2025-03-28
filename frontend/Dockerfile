FROM node:22.14-alpine
WORKDIR /frontend
COPY ./survey-taker-app .
RUN npm install
EXPOSE 5000
COPY . .
CMD ["npm", "start", "--debug"]