<template>
    <section>
      <div class="box">
        <div class="square" style="--i:0;"></div>
        <div class="square" style="--i:1;"></div>
        <div class="square" style="--i:2;"></div>
        <div class="square" style="--i:3;"></div>
        <div class="square" style="--i:4;"></div>
        <div class="square" style="--i:5;"></div>
        <div class="container">
          <div class="form">
            <h2 v-if="target === 1">用户注册</h2>
            <h2 v-if="target === 2">用户登录</h2>
            <h2 v-if="target === 3">找回密码</h2>
            <!-- 注册表单 -->
            <form v-if="target === 1" @submit.prevent="register">
              <div class="inputBx">
                <input type="text" v-model="registerData.username" required>
                <span>用户名</span>
                <i class="fa fa-user-circle"></i>
              </div>
              <div class="inputBx">
                <input type="tel" v-model="registerData.telephone" required>
                <span>手机号</span>
                <i class="fa fa-phone"></i>
              </div>
              <div class="inputBx password">
                <input id="register-password-input" type="password" v-model="registerData.password" required>
                <span>密码</span>
                <a href="#" class="password-control" @click="togglePasswordVisibility('register')"></a>
                <i class="fa fa-key"></i>
              </div>
              <div class="inputBx">
                <input type="text" v-model="registerData.real_name" required>
                <span>真实姓名</span>
                <i class="fa fa-user"></i>
              </div>
              <div class="inputBx">
                <input type="number" v-model="registerData.age" required>
                <span>年龄</span>
                <i class="fa fa-calendar"></i>
              </div>
              
              <div class="inputBx">
                <input type="email" v-model="registerData.mail" required>
                <span>邮箱</span>
                <i class="fa fa-envelope"></i>
              </div>
              <div class="inputBx">
                <input type="submit" value="注册">
              </div>
            </form>
            <!-- 登录表单 -->
            <form v-if="target === 2" @submit.prevent="login">
              <div class="inputBx">
                <input type="text" v-model="loginData.userortel" required>
                <span>用户名/手机号</span>
                <i class="fa fa-user-circle"></i>
              </div>
              <div class="inputBx password">
                <input id="login-password-input" type="password" v-model="loginData.password" required>
                <span>密码</span>
                <a href="#" class="password-control" @click="togglePasswordVisibility('login')"></a>
                <i class="fa fa-key"></i>
              </div>
              <div class="inputBx">
                <input type="submit" value="登录">
              </div>
            </form>
            <!-- 找回密码 -->
            <form v-if="target === 3" @submit.prevent="findback">
              <div class="inputBx">
                <input type="tel" v-model="findbackData.telephone" required>
                <span>手机号</span>
                <i class="fa fa-phone"></i>
              </div>
              <div class="inputBx password">
                <input id="findback-password-input" type="password" v-model="findbackData.password" required>
                <span>新密码</span>
                <a href="#" class="password-control" @click="togglePasswordVisibility('findback')"></a>
                <i class="fa fa-key"></i>
              </div>
              <div class="inputBx">
                <input type="submit" value="修改密码">
              </div>
            </form>
            <p v-if="target === 2">忘记密码? <a @click="target = 3">点击这里</a></p>
            <p v-if="target === 2">没有账号? <a @click="target = 1">注册</a></p>
            <p v-if="target === 3">已有账号? <a @click="target = 2">登录</a></p>
          </div>
        </div>
      </div>
    </section>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        target: 2, // 控制显示哪个表单 (1=注册, 2=登录, 3=找回密码)
        registerData: {
          username: '',
          telephone: '',
          password: '',
          real_name: '',
          age: null,
          sex: '男',
          mail: ''
        },
        loginData: {
          userortel: '',
          password: ''
        },
        findbackData: {
          telephone: '',
          password: ''
        },
        isRegisterPasswordVisible: false,
        isLoginPasswordVisible: false,
        isFindbackPasswordVisible: false
      };
    },
    methods: {
        async register() {
            try {
                const response = await axios.post("/user/register", this.registerData);
                if (response.data.status === 200) {
                    this.$message({
                        type: 'success',
                        message: '注册成功'
                    });
                    this.target = 2; // 切换到登录页面
                } else {
                    this.$message({
                        type: 'error',
                        message: response.data.msg
                    });
                }
            } catch (error) {
                console.error(error);
                this.$message({
                    type: 'error',
                    message: '注册失败'
                });
            }
        },
        async login() {
            try {
                const response = await axios.post("/user/login", this.loginData);
                if (response.data.code === 200) {
                    this.$message({
                        type: 'success',
                        message: '登录成功'
                    });
                    this.$router.push({ path: '/all_view' });
                } else {
                    this.$message({
                        type: 'error',
                        message: response.data.msg
                    });
                }
            } catch (error) {
                console.error(error);
                this.$message({
                    type: 'error',
                    message: '登录失败'
                });
            }
        },
        async findback() {
            try {
                const response = await axios.post("/user/findback", this.findbackData);
                if (response.data.status === 200) {
                    this.$message({
                        type: 'success',
                        message: '密码修改成功'
                    });
                    this.target = 2; // 切换到登录页面
                } else {
                    this.$message({
                        type: 'error',
                        message: response.data.msg
                    });
                }
            } catch (error) {
                console.error(error);
                this.$message({
                    type: 'error',
                    message: '修改密码失败'
                });
            }
        },
        togglePasswordVisibility(formType) {
            if (formType === 'register') {
                this.isRegisterPasswordVisible = !this.isRegisterPasswordVisible;
                const passwordInput = document.getElementById('register-password-input');
                passwordInput.type = this.isRegisterPasswordVisible ? 'text' : 'password';
            } else if (formType === 'login') {
                this.isLoginPasswordVisible = !this.isLoginPasswordVisible;
                const passwordInput = document.getElementById('login-password-input');
                passwordInput.type = this.isLoginPasswordVisible ? 'text' : 'password';
            } else if (formType === 'findback') {
                this.isFindbackPasswordVisible = !this.isFindbackPasswordVisible;
                const passwordInput = document.getElementById('findback-password-input');
                passwordInput.type = this.isFindbackPasswordVisible ? 'text' : 'password';
            }
        }
    }
};
</script>
  
  <style scoped>
  
  * {
    margin: 0;
    padding: 0;
    font-family: 'El Messiri', sans-serif;
  }
  
  body {
    background: #031323;
    overflow: hidden;
  }
  
  .fa {
    width: 32px;
  }
  
  section {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(-45deg, #7c40eb, #3071d1, #27b3cf, #50d1b3);
    background-size: 400% 400%;
    animation: gradient 10s ease infinite;
  }
  
  @keyframes gradient {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }
  
  .box {
    position: relative;
  }
  
  .box .square {
    position: absolute;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(5px);
    box-shadow: 0 25px 45px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 15px;
    animation: square 10s linear infinite;
    animation-delay: calc(-1s * var(--i));
  }
  
  @keyframes square {
    0%, 100% {
      transform: translateY(-20px);
    }
    50% {
      transform: translateY(20px);
    }
  }
  
  .box .square:nth-child(1) {
    width: 100px;
    height: 100px;
    top: -15px;
    right: -45px;
  }
  
  .box .square:nth-child(2) {
    width: 150px;
    height: 150px;
    top: 105px;
    left: -125px;
    z-index: 2;
  }
  
  .box .square:nth-child(3) {
    width: 60px;
    height: 60px;
    bottom: 85px;
    right: -45px;
    z-index: 2;
  }
  
  .box .square:nth-child(4) {
    width: 50px;
    height: 50px;
    bottom: 35px;
    left: -95px;
  }
  
  .box .square:nth-child(5) {
    width: 50px;
    height: 50px;
    top: -15px;
    left: -25px;
  }
  
  .box .square:nth-child(6) {
    width: 85px;
    height: 85px;
    top: 165px;
    right: -155px;
    z-index: 2;
  }
  
  .container {
    position: relative;
    padding: 50px;
    width: 260px;
    min-height: 380px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(5px);
    border-radius: 10px;
    box-shadow: 0 25px 45px rgba(0, 0, 0, 0.2);
  }
  
  .container::after {
    content: '';
    position: absolute;
    top: 5px;
    right: 5px;
    bottom: 5px;
    left: 5px;
    border-radius: 5px;
    pointer-events: none;
    background: linear-gradient(
        to bottom,
        rgba(255, 255, 255, 0.1) 0%,
        rgba(255, 255, 255, 0.1) 2%
    );
  }
  
  .form {
    position: relative;
    width: 100%;
    height: 100%;
  }
  
  .form h2 {
    color: #fff;
    letter-spacing: 2px;
    margin-bottom: 30px;
  }
  
  .form .inputBx {
    position: relative;
    width: 100%;
    margin-bottom: 20px;
  }
  
  .form .inputBx input {
    width: 80%;
    outline: none;
    border: none;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 10px;
    padding-left: 40px;
    border-radius: 15px;
    color: #fff;
    font-size: 16px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  }
  
  .form .inputBx .password-control {
    position: absolute;
    top: 11px;
    right: 10px;
    display: inline-block;
    width: 20px;
    height: 20px;
    background: url(https://snipp.ru/demo/495/view.svg) 0 0 no-repeat;
    transition: 0.5s;
  }
  
  .form .inputBx .password-control.view {
    background: url(https://snipp.ru/demo/495/no-view.svg) 0 0 no-repeat;
    transition: 0.5s;
  }
  
  .form .inputBx .fa {
    position: absolute;
    top: 13px;
    left: 13px;
  }
  
  .form .inputBx input[type="submit"] {
    background: #fff;
    color: #111;
    max-width: 100px;
    padding: 8px 10px;
    box-shadow: none;
    letter-spacing: 1px;
    cursor: pointer;
    transition: 1.5s;
  }
  
  .form .inputBx input[type="submit"]:hover {
    background: linear-gradient(115deg,
    rgba(0, 0, 0, 0.10),
    rgba(255, 255, 255, 0.25));
    color: #fff;
    transition: .5s;
  }
  
  .form .inputBx input::placeholder {
    color: #fff;
  }
  
  .form .inputBx span {
    position: absolute;
    left: 30px;
    padding: 10px;
    display: inline-block;
    color: #fff;
    transition: .5s;
    pointer-events: none;
  }
  
  .form .inputBx input:focus ~ span,
  .form .inputBx input:valid ~ span {
    transform: translateX(-30px) translateY(-25px);
    font-size: 12px;
  }
  
  .form p {
    color: #fff;
    font-size: 15px;
    margin-top: 5px;
  }
  
  .form p a {
    color: #fff;
  }
  
  .form p a:hover {
    background-color: #000;
    background-image: linear-gradient(to right, #434343 0%, black 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .remember {
    position: relative;
    display: inline-block;
    color: #fff;
    margin-bottom: 10px;
    cursor: pointer;
  }
  </style>