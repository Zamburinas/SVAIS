const url = 'ais.decodifier.uk.to';
const port = 9002;
import { Notify } from 'quasar';

export async function login(email, password) {
  return await fetch(`http://${url}:${port}/users/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      return response.json();
  })
  .then(data => {
    sessionStorage.setItem('token', data['token']);
    pushNotification('positive', 'Successfully logged in.')
    return true;
  })
  .catch(error => {
    pushNotification('negative', 'Wrong email/password.')
    return false;
  });
}

export async function register(userData) {
  return await fetch(`http://${url}:${port}/users/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(userData),
  })
  .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
  })
  .then(data => {
    pushNotification('positive', 'Successfully signed up.')
    return true;
  })
  .catch(error => {
    pushNotification('negative', 'Wrong data, please check.')
    return false;
  });
}

export async function checkToken() {
  return await fetch(`http://${url}:${port}/users/checkToken`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",    },
    body: JSON.stringify({
      token: sessionStorage.getItem('token'),
    }),
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      return response.json();
  })
  .then(data => {
    return true;
  })
  .catch(error => {
    return false;
  });
}

export function pushNotification(color, message) {
  Notify.create({
    color: color, 
    message: message,
    position: 'top-right',
    actions: [
      {
        icon: 'close', 
        color: 'white', 
        round: true
      }
    ]
  });
}