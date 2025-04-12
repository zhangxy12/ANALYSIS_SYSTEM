<template>
  <dv-border-box-2>
    <div class="rumor-detection-container">
      <h1>谣言检测</h1>
      <div class="input-section">
        <input
          v-model="inputText"
          type="text"
          placeholder="输入要检测的文本"
          class="input-field"
        />
        <button @click="detectRumor" class="detect-button">检测</button>
      </div>
      <div v-if="result!== null" class="result-section">
        <p :class="{ 'is-rumor': result === 0, 'not-rumor': result === 1 }">
          {{ result === 1? '可能不是谣言' : '疑似谣言' }}
        </p>
      </div>
    </div>
  </dv-border-box-2>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        inputText: '',
        result: null
      };
    },
    methods: {
      async detectRumor() {
        try {
          const response = await axios.get('/rumor/rumor_detect', {
            params: {
              text: this.inputText
            }
          });
          this.result = response.data.data.is_rumor;
          console.log(this.result);
        } catch (error) {
          console.error('检测失败:', error);
          this.result = null;
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .rumor-detection-container {
    margin-top: 0px;
    font-family: Arial, sans-serif;
    background: #ffffff00;
    /* display: flex; */
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 50px;
  }
  
  h1 {
    color: white;
    margin-top: 0px;
  }
  
  .input-section {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .input-field {
    padding: 10px;
    font-size: 16px;
    border: none;
    border-radius: 4px;
    width: 300px;
    margin-right: 10px;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
  }
  
  .detect-button {
    padding: 10px 20px;
    font-size: 16px;
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
  }
  
  .detect-button:hover {
    background-color: #1976D2;
  }
  
  .result-section {
    margin-bottom: 10px;
    color: white;
    font-size: 18px;
  }
  
  .is-rumor {
    color: #fcfaf9;
  }
  
  .not-rumor {
    color: #f1f7f1;
  }
  </style>