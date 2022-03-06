import logo from './logo.svg';
import './App.css';

// import HeaderSteps from './components/Steps/Steps';
import LandingPage from './pages/LandingPage/LandingPage';

function App() {
  return (
    <div className="App">
      <LandingPage />
    </div>
  );
}

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//       <LandingPage />
//     </div>
//   );
// }

export default App;
