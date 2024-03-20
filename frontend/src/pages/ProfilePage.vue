<template>
    <div class="profile-container">
      <div class="profile">
        <div class="avatar">
          <img src="https://via.placeholder.com/150" alt="Avatar">
        </div>
        <div class="info">
          <!-- Nombre del usuario -->
          <h1 class="name">{{ user.name }}</h1>
      
          <!-- Correo electrónico -->
          <p>Email: {{ user.email }}</p>
      
          <!-- Edad -->
          <p>Edad: {{ user.age }}</p>
      
          <!-- País -->
          <p>País: {{ user.country }}</p>
      
          <!-- Mostrar una lista de intereses -->
          <h2>Intereses:</h2>
          <ul>
            <li v-for="(interest, index) in user.interests" :key="index">{{ interest }}</li>
          </ul>
  
          <!-- Botón para activar la autenticación por identificación facial -->
          <button @click="activateFacialRecognition" class="facial-auth-button">Activar Autenticación Facial</button>
        </div>
      </div>
    </div>
  </template>
    
  <script>
  export default {
    data() {
      return {
        user: {
          name: 'John Doe',
          email: 'johndoe@example.com',
          age: 30,
          country: 'United States',
          interests: ['Programming', 'Hiking', 'Reading']
        }
      };
    },
    methods: {
      activateFacialRecognition() {
        // Aquí puedes agregar la lógica para activar la autenticación por identificación facial
        alert('Autenticación por identificación facial activada');
      }
    }
  };
  </script>
    
  <style scoped>
  .profile-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .profile {
    width: 80%;
    max-width: 600px;
    padding: 20px;
    border-radius: 8px;
    display: flex;
    align-items: center;
  }
  
  .avatar {
    flex: 0 0 auto;
    margin-right: 20px;
  }
  
  .avatar img {
    width: 150px;
    height: 150px;
    border-radius: 50%;
  }
  
  .info {
    flex: 1 1 auto;
  }
  
  .name {
    font-size: 2em; /* Letras más grandes */
  }
  
  .profile p {
    margin-bottom: 10px; /* Separación más grande entre párrafos */
  }
  
  .profile h2 {
    margin-top: 20px;
    margin-bottom: 10px;
  }
  
  .profile ul {
    margin-left: 20px;
  }
  
  .facial-auth-button {
    background-color: #2196f3;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .facial-auth-button:hover {
    background-color: #0c7bb3;
  }
  </style>
  