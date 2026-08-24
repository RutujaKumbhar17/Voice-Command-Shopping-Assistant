-- MySQL dump 10.13  Distrib 9.0.1, for macos14 (x86_64)
--
-- Host: localhost    Database: farmpure
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `buyerregistration`
--

DROP TABLE IF EXISTS `buyerregistration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buyerregistration` (
  `buyer_id` int NOT NULL AUTO_INCREMENT,
  `buyer_name` varchar(30) NOT NULL,
  `buyer_phone` bigint NOT NULL,
  `buyer_addr` text NOT NULL,
  `buyer_comp` varchar(100) NOT NULL,
  `buyer_license` varchar(100) NOT NULL,
  `buyer_bank` int NOT NULL,
  `buyer_pan` varchar(10) NOT NULL,
  `buyer_mail` varchar(20) NOT NULL,
  `buyer_username` varchar(20) NOT NULL,
  `buyer_password` varchar(20) NOT NULL,
  PRIMARY KEY (`buyer_id`),
  UNIQUE KEY `buyer_username` (`buyer_username`),
  UNIQUE KEY `buyer_phone` (`buyer_phone`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buyerregistration`
--

LOCK TABLES `buyerregistration` WRITE;
/*!40000 ALTER TABLE `buyerregistration` DISABLE KEYS */;
INSERT INTO `buyerregistration` VALUES (1,'Abhi',1234567890,' Raj Nagar','Elysian.org','02082000',2147483647,'1234567890','abhi@hmil.com','admin','1111'),(2,'Arpit',7666610976,'Bhat Mansion','Mafia Pvt Ltd','99',12345,'987','arpit@gmail.com','redhawk','2222'),(3,'Kishori',2589631472,'Vadala','apple','w3566908',8947,'2436467897','kishori@gmail.com','melissa','3333'),(4,'Lokesh',9029788504,'SEC -13','VLCC Pvt Ltd','MAHARASHTRA',0,'1234567890','abhi@hmil.com','lokesh','4444'),(5,'Ansh',9819104641,'fam','Elysian.org','MAHARASHTRA',2147483647,'1234567890','abhi@hmil.com','ansh','5555'),(20,'bhabalomkar421',8828071232,'bj','c company','just **** off',1,'1','xyz@domain.com','501807','yw==');
/*!40000 ALTER TABLE `buyerregistration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `product_id` int NOT NULL,
  `phonenumber` bigint NOT NULL,
  `qty` int NOT NULL DEFAULT '1',
  `subtotal` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (32,8169193101,2,10);
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `cat_id` int NOT NULL AUTO_INCREMENT,
  `cat_title` varchar(100) NOT NULL,
  PRIMARY KEY (`cat_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Crops'),(2,'Vegetables'),(3,'Fruits');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consumer`
--

DROP TABLE IF EXISTS `consumer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `email` varchar(20) NOT NULL,
  `pincode` varchar(10) NOT NULL,
  `password` varchar(10) NOT NULL,
  `address` varchar(50) NOT NULL,
  `phone` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumer`
--

LOCK TABLES `consumer` WRITE;
/*!40000 ALTER TABLE `consumer` DISABLE KEYS */;
INSERT INTO `consumer` VALUES (5,'bhabalomkar421','bhabalomkar421@gmail','421202','yw==','m','8828071232'),(6,'hello world','hello@world.com','421202','yw==','world','9999999999'),(7,'Abhishek Gupta','abhig0209@gmail.com','400705','m8bf5+Y=','Test','1234567890'),(8,'int main','intmain@g.com','400705','yw==','704,Raj Uday CHS , Sec-1\r\nSanpada','7715802258');
/*!40000 ALTER TABLE `consumer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `farmerregistration`
--

DROP TABLE IF EXISTS `farmerregistration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `farmerregistration` (
  `farmer_id` int NOT NULL AUTO_INCREMENT,
  `farmer_name` varchar(255) NOT NULL,
  `farmer_phone` bigint NOT NULL,
  `farmer_address` text NOT NULL,
  `farmer_state` varchar(50) NOT NULL,
  `farmer_district` varchar(50) NOT NULL,
  `farmer_pan` varchar(10) NOT NULL,
  `farmer_bank` bigint NOT NULL,
  `farmer_password` varchar(100) NOT NULL,
  PRIMARY KEY (`farmer_id`),
  UNIQUE KEY `farmer_id` (`farmer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `farmerregistration`
--

LOCK TABLES `farmerregistration` WRITE;
/*!40000 ALTER TABLE `farmerregistration` DISABLE KEYS */;
INSERT INTO `farmerregistration` VALUES (1,'Abhishek',8169193101,'Kolad','MAHARASHTRA','thane','1234567890',2147483647,'111'),(2,'Raghav',9101891234,'Kewad','MAHARASHTRA','Misrod','1234567890',1141473247,'222'),(3,'Omkar',8169193102,'Palm Beach Road','Kerala','Alapuzzha','123ABC',45745425,'333'),(4,'Ram',8169193103,'Gang Vihar','MAHARASHTRA','Nagpur','123ABC',211324654,'444'),(5,'Lokesh',8169193104,'Sec-15 Newtown Road','MAHARASHTRA','Nagpur','1325355',45745425,'555'),(6,'Ramlal',8169193105,'Jodhivir','WEST BENGAL','Darjiling','1234567899',2147483647,'666'),(7,'Chirag',8169193106,'Uptown','WEST BENGAL','Darjiling','5341874510',2147483647,'777'),(8,'Shyam',8169193107,'Mahanagar','WEST BENGAL','Jalpaiguri','6846516843',2147483647,'888'),(9,'Neeta',8169193108,'Lodi Nagar','HIMACHAL PRADESH','Chamba','3263062',56878613,'999'),(10,'Meeta',8169193109,'Area Colony','HIMACHAL PRADESH','Kullu','2983473057',2147483647,'1010'),(11,'Yeha',8169193110,'Habibganj','HIMACHAL PRADESH','Kullu','65416541',454586125,'1111'),(12,'Arpan',8169193111,'Dehradhun','HIMACHAL PRADESH','Chamba','24685435',248654352,'1212'),(13,'Anshika',8169193112,'Devnagar','HIMACHAL PRADESH','Solan','45674852',3216415,'1313'),(14,'Devanand',8169193113,'Shikhar','HIMACHAL PRADESH','Solan','246856873',2147483647,'1414'),(15,'Indrapuri',8169193113,'Kewad','HIMACHAL PRADESH','Guwahati','246856873',2147483647,'1515'),(16,'Saket Nagar',8169193114,'Bujhaneet','LAKSHADWEEP','Lakshadweep','3549685416',65464851,'1616'),(17,'Rinda',8169193115,'Lodi Nagar','LAKSHADWEEP','Rizwa','2456435',21544232,'1717'),(18,'Raghuram',8169193116,'Rajwada','MADHYA PRADESH','Rewa','574542',3846835,'1818'),(19,'Sansuram',8169193117,'Panji','GOA','North Goa','2456843',3468651,'1919'),(20,'Kishori',8169193118,'Rohitnagar','GOA','North Goa','274635213',27486513,'2020'),(21,'Ramlal',8169193119,'Kashi','GOA','South Goa','24756215',24568536,'2121'),(22,'Arya',8169193120,'Regal Town','GOA','South Goa','2458742884',249685547,'2222'),(23,'Sunil',8169193121,'Meghpur','HARYANA','Rohtak','255451025',54564684,'2323'),(24,'Ashwin',8169193121,'Meghpur','HARYANA','Rk Nagar','255451025',54564684,'2424'),(25,'Anil Lal Kishori',8169193122,'Kothri','DAMAN AND DIU','Diu','54584646.',541564564,'2525'),(26,'Mohanlal',8169193123,'Vibhuti Nagar','DAMAN AND DIU','Daman','2545498',524845638,'2626'),(27,'Kishanlal',8169193124,'Khajurikalan','TAMIL NADU','Nagapattinam','54584636',254685746,'2727'),(28,'Rampyare',8169193121,'Meghpur','HARYANA','Rk Nagar','255451025',54564684,'2828'),(29,'Pyarelal',8169193125,'Rohitnagar','JHARKAND','Garhwa','656',168,'yw=='),(30,'RaviKishan',8169193126,'Vihar','JHARKAND','Garhwa','54664851',6455415,'3030'),(31,'Swaarop',8169193127,'Kalan','JHARKAND','Garhwa','6416545',4646544,'3131'),(32,'Jesudas',8169193128,'Shiv Sadar','JHARKAND','Palamu','4515214',544613515,'3232'),(33,'Prakash',8169193129,'Ayodhya','JAMMU AND KASHMIR','Kupwara','1232122121',121321,'3333'),(34,'Mitesh',8169193130,'19/502, Sector 11  Koparkhairne','MAHARASHTRA','Nandurbar','656861651',5465415,'3434'),(35,'Manav',8169193131,'19/502Fam','JAMMU AND KASHMIR','Kupwara','656861651',5465415,'3535'),(36,'Manya',8169193132,'Rewa','JAMMU AND KASHMIR','Baramula','6568616510',54654101,'3636'),(37,'Raghavlal',8169193133,'Khajuri','JAMMU AND KASHMIR','Baramula','6568616510',54654101,'3737'),(38,'Ramlal',8169193134,'Yonapur','JAMMU AND KASHMIR','Srinagar','123123123',3213213,'3838'),(39,'Jhunjhun',8169193135,'Juhi','JAMMU AND KASHMIR','Srinagar','121212121',1212,'3939'),(40,'Mukesh',8169193136,'Neela','JAMMU AND KASHMIR','Badgam','121212',121211,'4040');
/*!40000 ALTER TABLE `farmerregistration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `qty` int NOT NULL,
  `address` varchar(255) NOT NULL,
  `delivery` varchar(10) NOT NULL,
  `phonenumber` bigint NOT NULL,
  `total` int NOT NULL,
  `payment` varchar(10) NOT NULL,
  `buyer_phonenumber` bigint NOT NULL,
  PRIMARY KEY (`order_id`),
  KEY `product_id` (`product_id`),
  KEY `phonenumber` (`phonenumber`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (55,23,1,' Raj Uday 234','Buyer',8169193101,56,'cod',1234567890),(56,28,1,' Raj Uday 234','Buyer',8169193101,45,'cod',1234567890),(57,31,1,'I am Hungry','Buyer',8169193101,25,'cod',1234567890),(58,3,2,' Raj Uday 234','Farmer',8169193101,10,'paytm',1234567890),(60,32,1,'Working','Buyer',8169193101,10,'cod',1234567890);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_id` int NOT NULL AUTO_INCREMENT,
  `farmer_fk` int NOT NULL,
  `product_title` varchar(100) NOT NULL,
  `product_cat` varchar(100) NOT NULL,
  `product_type` varchar(100) NOT NULL,
  `product_expiry` varchar(25) NOT NULL,
  `product_image` text NOT NULL,
  `product_stock` int NOT NULL,
  `product_price` int NOT NULL,
  `product_desc` text NOT NULL,
  `product_keywords` text NOT NULL,
  `product_delivery` varchar(5) NOT NULL,
  PRIMARY KEY (`product_id`),
  KEY `farmer_fk` (`farmer_fk`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,1,'Ramlal Potato','2','Potato','2020-04-15','Potato.jpg',1000,12,'Best Quality product guarented 100 percent','potato','yes'),(3,1,'Ramlal Tomato','2','Tomato','2020-04-15','Tomato.jpg',500,5,'Best Quality toamato assured','tomato , best quality tomato , Ramlal Tomato','no'),(17,3,'Shivneri Bananas','3','Bananas','2020-04-15','Bananas.jpg',250,30,'Best Quality Bananas','banana, shivneri ,','yes'),(18,3,'Ram Rice','1','Rice','2020-04-15','Rice.jpg',1500,2,'waqd','best rice','yes'),(19,1,'Ansh Carrot','2','Carrot','2020-04-15','Carrot.jpg',1250,56,'Big fat juicy best quality carrots assured','carrot,best carrot','yes'),(21,1,'Abhi Maize','1','Maize','2020-04-15','Maize.jpg',750,99,'Seeds Import from australia , grown with love','Maize,best Maize','yes'),(22,3,'Calista Coconut','1','Coconut','2020-04-15','Coconut.jpg',450,12,'Better than others','Coconut,best Coconut','no'),(23,1,'Arpit Grapes','3','Grapes','2020-04-15','Green Grapes.jpg',4560,56,'Best Grapes you will ever find','grapes,green grapes,best grapes','yes'),(24,1,'Arpit Apples','3','Apple','2020-04-15','Apple.jpg',1500,101,'Best Apples grown in Kashmir and handled with love and care','apples,apple,best apple','no'),(25,1,'Ramlal Wheat','1','Wheat','2020-04-15','Wheat.jpg',2000,80,'Thin , Fragrant wheat grains grown with love','wheat,best quality wheat,best wheat','no'),(27,3,'Arpit Alphonso Mango','3','Mango','2020-04-15','Mango.jpg',2000,200,'Grown with love in Ratnagiri','mango,alponso mango,best mango','yes'),(28,1,'Ansh Custard Apple','3','Custard Apple','2020-04-15','custartapple.cms',500,45,'Custard Apple so tasty ,to die for','Custard Apple,custart apple, apple, best custard apple','yes'),(29,3,'Omkar Cabbage','2','Cabbage','2020-04-15','Cabbage.jpg',1500,50,'Best Quality Cabbage','cabbage, best Cabbage','yes'),(30,1,'Ansh Onion','2','Onion','2020-04-15','Onion.jpg',1500,65,'Grown with love','Onion,best onion','no'),(31,1,'Abhi Strawberry','3','Strawberry','2020-04-15','strawberry.jpg',100,25,'Best Strawberrys all over India ','Strawberry,best strawberry','yes'),(32,1,'Abhi Orange','3','Orange','2020-04-15','orange.jpg',1500,10,'Best Oranges grown with love in Nagpur','Orange,best Orange','yes'),(37,1,'Ram Sugacane','1','Sugarcane','2020-04-25','Sugarcane.jpg',1000,50,'Best Sugarcane','Sugarcane','yes');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shopkeeper`
--

DROP TABLE IF EXISTS `shopkeeper`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shopkeeper` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `email` varchar(20) NOT NULL,
  `pincode` varchar(6) NOT NULL,
  `password` varchar(10) NOT NULL,
  `shopName` varchar(20) NOT NULL,
  `shopAddress` varchar(50) NOT NULL,
  `phone` varchar(10) NOT NULL,
  `startTime` varchar(8) NOT NULL,
  `endTime` varchar(8) NOT NULL,
  `slotInterval` int NOT NULL,
  `slotUser` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shopkeeper`
--

LOCK TABLES `shopkeeper` WRITE;
/*!40000 ALTER TABLE `shopkeeper` DISABLE KEYS */;
INSERT INTO `shopkeeper` VALUES (1,'bhabalomkar421','bhabalomkar421@gmail','421202','yw==','xyz','xyz','8828071232','10:30','12:30',30,5),(3,'int main 123','intmain1221@gmail.co','400705','yw==','hopes','no hopes','101','10:30','11:30',30,7),(4,'kerela','es@dd.com','421200','yw==','1','m','8369674856','10:00','12:30',60,5),(5,'Abhishek Gupta','abhig0209@gmail.com','400705','m8bf5+Y=','Ganesh Grocery','Rose Villa Lane','1234567890','12:00','22:00',30,5),(6,'omkar bhabal','intmain1221@gmail.co','400705','yw==','om medical','navapada','9223152967','10:30','17:00',30,5),(7,'Ganesh','ganesh@mail.com','123456','m8bf5+Y=','Ganesh Grocery','Mumbai','1234567891','10:00','14:00',30,5);
/*!40000 ALTER TABLE `shopkeeper` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-20 22:51:41
