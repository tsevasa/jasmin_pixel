folder = getDirectory("Wähle einen Ordner");
list = getFileList(folder);
	length= lengthOf(list);
a=0;
b=1;
IDcounter = 0;

// BENUTZEREINSTELLUNGEN
expandSize = 1.5; // Größe des perinukleären Bereichs (Pixel)
shrinkSize = 0.5; // Größe des perinukleären Bereichs (Pixel)
//Min/Max für die Intensitätsbilder setzen
Dialog.create("Min/Max für die Intensitätsbilder setzen");
Dialog.addNumber("Minimum:", 0);
Dialog.addNumber("Maximum:", 10000);
Dialog.show();
min = Dialog.getNumber();
max = Dialog.getNumber();
//Initialisieren des Zielortes
outputPath = getDirectory("Choose a folder to save results") + "Intensity_Results2.csv";
File.saveString("ID,PerinuclearIntensity,Name", outputPath); // CSV-Header
//öffnen mehrerer Bildpaare in einem Ordner

for(j=0;  j<length/2; j=j+1){
	//rois löschen
	if (roiManager("Count") > 0) {
    roiManager("reset");
}
//Bildnahmen für den Algorithmus einziehen
name= list[a];
name2= list[b];
open(folder + name);
title2 = getTitle();
open(folder + name2);
title1 = getTitle();
a=a+2;
b=b+2;

// Nucleus-Bild duplizieren
selectWindow(title1);
run("Duplicate...", "title=Nuclei_Processing");

// Intensitätsbild duplizieren
selectWindow(title2);
run("Duplicate...", "title=Intensity_Processing");

// **Bildvorverarbeitung: Glätten und Kontrast anpassen**
selectWindow("Nuclei_Processing");

run("Threshold...");//Treshold einstellen für nuclei
waitForUser("Bitte Schwellenwert anpassen und 'OK' klicken, um fortzufahren.");
run("Convert to Mask"); // Maske erstellen


// Zellkerne segmentieren
run("ROI Manager...");
run("Analyze Particles...", "size=30.00-Infinity circularity=0.50-1.00 add");

// Nuclei zählen
roiCount = roiManager("count");
run("Clear Results"); // Ergebnisse für nächste Messung löschen

// Wechsel zum Intensitätsbild für Messung
selectWindow("Intensity_Processing");
setMinAndMax(min, max);
run("Apply LUT");

// Perinukleäre Regionen erweitern und messen
for (i = 0; i < roiCount; i++) {
    roiManager("Select", i);
    run("Enlarge...", "enlarge=" + (-shrinkSize));
    roiManager("Add"); // Neue perinukleäre ROI speichern
}

// Array mit Indizes von 1 bis roicount2 erstellen (also 1 bis einschließlich 30)
indices = newArray(roiCount);
for (i = 0; i < roiCount; i++) {
    indices[i] = i + 1;
}
//alte ROIS löschen
roiManager("Select", indices);
roiManager("Delete");

// Perinukleäre Regionen erweitern und messen
for (i = 0; i < roiCount; i++) {
    roiManager("Select", i);
    run("Enlarge...", "enlarge=" + expandSize);
    roiManager("Add"); // Neue perinukleäre ROI speichern
}
roiCount2 = roiManager("count");

for (i = 0; i < roiCount; i++) {
    roiManager("Select", newArray(i, i+roiCount)); // beide ROIs auswählen
roiManager("XOR"); // Differenz (XOR) erzeugen
 roiManager("Add"); // Neue perinukleäre ROI speichern
}
// Array mit Indizes von 1 bis roicount2 erstellen (also 1 bis einschließlich 30)
indices = newArray(roiCount2);
for (i = 0; i < roiCount2; i++) {
    indices[i] = i + 1;
}
roiManager("Select", indices);
roiManager("Delete");

// Messung der perinukleären Intensität
roiManager("Deselect");
selectWindow("Intensity_Processing");

// Messung der perinukleären Intensität
roiManager("Deselect");
roiManager("Measure");
print(" gemessen ");

// Werte für nukleäre Intensität abrufen
perinuclearIntensities = newArray(roiCount);
for (c = 0; c < roiCount; c++) {
    perinuclearIntensities[c] = getResult("Mean", c);
}

run("Clear Results");
roiManager("Select", "all"); 
roiManager("delete");
print("rois deleted");
close("*");
// Ergebnisse in CSV speichern

File.append("", outputPath);

for (i = 0; i < perinuclearIntensities.length; i++) {
    id = i + 1; // IDs beginnen bei 1
    intensity1 = perinuclearIntensities[i];
    
    File.append(id + "," + intensity1  + ","+  name + "\n", outputPath);
}
 
}
print("✅ Analyse abgeschlossen! Ergebnisse gespeichert unter: " + outputPath);
exit;
