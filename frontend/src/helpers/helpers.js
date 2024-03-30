const url = 'localhost';
const port = 9002;
import { Notify, SessionStorage } from 'quasar';

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
    .then(async response => {
      if (!response.ok) {
        let responseJson = await response.json();
        let message = responseJson.msg;
        throw new Error(message);
      }
      return response.json();
    })
    .then(data => {
      saveToken(data);
      // SessionStorage.set('token', data['token']);
      // authenticated();
      pushNotification('positive', 'Successfully logged in.', 'top')
      return true;
    })
    .catch(error => {
      pushNotification('negative', error.message)
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
    .then(async response => {
      if (!response.ok) {
        let responseJson = await response.json();
        let message = responseJson.msg;
        throw new Error(message);
      }
      return response.json();
    })
    .then(data => {
      pushNotification('positive', 'Successfully signed up.');
      return true;
    })
    .catch(error => {
      pushNotification('negative', error.message);
      return false;
    });
}

export async function checkToken() {
  return await fetch(`http://${url}:${port}/users/checkToken`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      token: SessionStorage.getItem('token'),
    }),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      authenticated();
      return true;
    })
    .catch(error => {
      notAuthenticated();
      return false;
    });
}

export async function logout(router, authObject = ref) {
  pushNotification(
    'light-blue',
    'Are you sure want to logout?',
    'top',
    [
      {
        label: 'Yes', color: 'white', handler: () => {
          deleteToken();
          router('/login')
        }
      },
      { label: 'No', color: 'white', handler: () => { /* ... */ } }
    ]
  )
}

export function pushNotification(color,
  message,
  position = 'top-right',
  actions = [{
    icon: 'close',
    color: 'white',
    round: true
  }]) {
  Notify.create({
    color: color,
    message: message,
    position: position,
    actions: actions
  });
}


export async function getAllCoords() {
  return await fetch(`http://${url}:${port}/coords/coords`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
}

export async function getBoatInfo() {
  return await fetch(`http://${url}:${port}/coords/boat_info`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
}

export async function getBoatRoute(boatName) {
  return await fetch(`http://${url}:${port}/coords/get_route`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }, body: JSON.stringify(boatName),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
}

export async function getProtectedAreas() {
  return await fetch(`http://${url}:${port}/coords/getProtectedAreas`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    },
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
}

export async function sendImageToBackend(imageFile) {
  return await fetch(`http://${url}:${port}/users/twoFactorAuth`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      image: imageFile.split(',')[1],
    }),
  }).then(async response => {
    if (!response.ok) {
      let responseJson = await response.json();
      let message = responseJson.msg;
      throw new Error(message);
    }
    return response.json();
  })
    .then(data => {
      pushNotification('positive', data.message, 'top')
      return true;
    })
    .catch(error => {
      pushNotification('negative', error.message, 'top')
      return false;
    });


}

function authenticated() {
  window.dispatchEvent(new CustomEvent('Auth'));
}

function notAuthenticated() {
  window.dispatchEvent(new CustomEvent('notAuth'));
}

function saveToken(data) {
  SessionStorage.set('token', data['token']);
  SessionStorage.set('user', data['user_info']);
  authenticated();
}

function deleteToken() {
  SessionStorage.remove('token');
  SessionStorage.remove('user');
  notAuthenticated();
}