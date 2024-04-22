const url = 'localhost:9002/api';
import { Notify, SessionStorage } from 'quasar';

export async function login(email, password, tfa) {
  return await fetch(`http://${url}/users/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: email,
      password: password,
      tfa: tfa.split(',').length === 2 ? tfa.split(',')[1] : tfa.split(',')[0]
    }),
  })
    .then(async response => {
      if (!response.ok) {
        let responseJson = await response.json();
        let message = responseJson.msg;
        if (responseJson.tfa) {
          askTwoFactorAuth();
        }
        throw new Error(message);
      }
      return response.json();
    })
    .then(data => {
      saveToken(data);
      pushNotification('positive', 'Successfully logged in.', 'top')
      return true;
    })
    .catch(error => {
      pushNotification('negative', error.message)
      return false;
    });
}

export async function register(userData) {
  return await fetch(`http://${url}/users/register`, {
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
      pushNotification('positive', data.message);
      return true;
    })
    .catch(error => {
      pushNotification('negative', error.message);
      return false;
    });
}

export async function checkToken() {
  return await fetch(`http://${url}/users/checkToken`, {
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

export async function logout(router) {
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
  position = 'top',
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
  return await fetch(`http://${url}/coords/coords`, {
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

export async function getBoatNames() {
  return await fetch(`http://${url}/coords/boat_names`, {
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
  return await fetch(`http://${url}/coords/get_route`, {
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

export async function getBoatInfo(boatName) {
  return await fetch(`http://${url}/coords/boatInfo`, {
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

export async function getBoats(boatName) {
  return await fetch(`http://${url}/coords/boat_names`, {
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
  return await fetch(`http://${url}/coords/getProtectedAreas`, {
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

export async function sendImageToBackend(imageFile, password) {
  return await fetch(`http://${url}/users/twoFactorAuth`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      image: imageFile.split(',')[1],
      email: SessionStorage.getItem('user').email,
      password: password
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

export async function takePhoto() {
  try {
    // Access the user's camera
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });

    // Create a video element to display the camera stream
    const videoElement = document.createElement('video');
    videoElement.srcObject = stream;
    videoElement.autoplay = true;

    // Wait for the video to load
    await new Promise(resolve => videoElement.onloadedmetadata = resolve);

    // Create a canvas element to capture the image
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    // Draw the video frame on the canvas
    const context = canvas.getContext('2d');
    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    // Stop the camera stream
    stream.getVideoTracks().forEach(track => track.stop());

    // Convert the canvas image to a data URL
    const dataUrl = canvas.toDataURL('image/png');


    // Set the captured image
    return dataUrl;

  } catch (error) {
    console.error('Error capturing image:', error);
  }
}

export async function disableTwoFactor(password) {
  return await fetch(`http://${url}/users/disableTwoFactor`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: SessionStorage.getItem('user').email,
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
      pushNotification('positive', data.message, 'top')
      return true;
    })
    .catch(error => {
      pushNotification('negative', error.message)
      return false;
    });
}

export async function uploadFile(formData) {
  return await fetch(`https://${url}/coords/decodeFile`, {
    method: "POST",
    body: formData
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
    pushNotification('positive', data.msg, 'top')
    return data;
  })
  .catch(error => {
    pushNotification('negative', error.message)
    return {};
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

function askTwoFactorAuth() {
  SessionStorage.set('required', { 'tfa': true });
  window.dispatchEvent(new CustomEvent('tfa'));
}