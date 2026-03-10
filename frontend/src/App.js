import './App.css';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
      </header>

      <div className = "container">
        <div className='map-section'>
          <div className="map-frame-wrapper">
            <div className="map-frame">
              <MapContainer 
                center={[36.2048, 138.2529]}   
                zoom={6}                        
                className="map-frame"           
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
              </MapContainer>
            </div>
          </div>
        </div>
        
        <div className='resorts-section'>
          
        </div>
      </div>

    </div>
  );
}

export default App;
