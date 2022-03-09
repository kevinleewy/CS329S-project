import './App.css';

import HomePage from './pages/HomePage/HomePage';

function App() {
  window.onunload = function () {
    sessionStorage.removeItem("dontShowWelcomeModal");
    sessionStorage.removeItem("showMensClothes");
    sessionStorage.removeItem("showWomensClothes");
  }

  sessionStorage.showMensClothes = true;
  sessionStorage.showWomensClothes = true;

  return (
    <div className="App">
      <HomePage />)
    </div>
  );
}

export default App;
