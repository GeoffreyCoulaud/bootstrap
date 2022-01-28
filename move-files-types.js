const path = require("path");
const fs = require("fs");

const root = process.argv[2];
const recupPrefix = process.argv[3];

const DRY = false;
const FORBIDDEN_EXT_DIRS = [
	"",
	".",
	".."
];

function main(){

	// Get all dirs that are direct children of root
	const dirsList = fs.readdirSync(root, {withFileTypes: true})
		.filter(ent => ent.isDirectory() && ent.name.startsWith(recupPrefix));
	
	// For all dir, move files in their appropriate destination
	for (const dir of dirsList){
		const dirPath = path.join(root, dir.name);
	
		// List and loop through files
		const filesDirentList = fs.readdirSync(dirPath, {withFileTypes: true})
			.filter(ent => ent.isFile());
		for (const fileDirent of filesDirentList){
			

			let ext = path.extname(fileDirent.name)
				.replace(".", "")
				.toLowerCase();
			if (FORBIDDEN_EXT_DIRS.includes(ext)){
				ext = "NOEXT";
			}
			const source = path.join(dirPath, fileDirent.name);
			const destinationDir = path.join(root, ext);
			const destination = path.join(destinationDir, fileDirent.name);
			console.log(`Moving ${source} => ${destination}`);
			
			// Create dir for this extension if it doesn't exist
			if (!fs.existsSync(destinationDir)){
				fs.mkdirSync(destinationDir);
			}
			
			// Move file into its type dir
			if(!DRY){
				fs.renameSync(source, destination);
			}
		}
	}
	
	console.log("Done.");

}

if (DRY){
	console.log("DRY RUN : No files will be moved");
	console.log("--------------------------------")
}
console.log(`Will move every file in ${root}/*/ to a ${root}/extname/`);
main();