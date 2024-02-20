const url = 'localhost';
const port = 9002;
import { Notify } from 'quasar';

export function login(email, password) {
  fetch(`http://${url}:${port}/users/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
        "Authorization": localStorage.getItem('token')
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
      // If the response is successful, you might want to handle it here
      // For example, you can check the response status or data
      return response.json();
  })
  .then(data => {
    localStorage.setItem('token', data['token']);
    pushNotification('positive', 'Successfully logged in.')
  })
  .catch(error => {
    pushNotification('negative', 'Wrong email/password.')
  });
}

export async function checkToken() {
  fetch(`http://${url}:${port}/users/checkToken`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",    },
    body: JSON.stringify({
      token: localStorage.getItem('token'),
    }),
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      // If the response is successful, you might want to handle it here
      // For example, you can check the response status or data
      return response.json();
  })
  .then(data => {
    return true;
  })
  .catch(error => {
    // Handle fetch errors here
    return false;
  });
}

function pushNotification(color, message) {
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