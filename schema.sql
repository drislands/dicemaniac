-- MySQL dump 10.16  Distrib 10.1.20-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: localhost
-- ------------------------------------------------------
-- Server version	10.1.20-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `default_moves`
--

DROP TABLE IF EXISTS `default_moves`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `default_moves` (
  `name` varchar(10) DEFAULT NULL,
  `stat1` varchar(10) DEFAULT NULL,
  `val1` varchar(10) DEFAULT NULL,
  `stat2` varchar(10) DEFAULT NULL,
  `val2` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `default_moves`
--

LOCK TABLES `default_moves` WRITE;
/*!40000 ALTER TABLE `default_moves` DISABLE KEYS */;
INSERT INTO `default_moves` VALUES ('fast','min damage','1','max damage','2'),('strn','min damage','3','max damage','4'),('dfnd','health','1',NULL,NULL);
/*!40000 ALTER TABLE `default_moves` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `duel_history`
--

DROP TABLE IF EXISTS `duel_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `duel_history` (
  `player1` varchar(15) DEFAULT NULL,
  `player2` varchar(15) DEFAULT NULL,
  `active` int(1) NOT NULL DEFAULT '0',
  `winner` varchar(15) DEFAULT NULL,
  `duelid` varchar(32) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `duel_history`
--

LOCK TABLES `duel_history` WRITE;
/*!40000 ALTER TABLE `duel_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `duel_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `duels`
--

DROP TABLE IF EXISTS `duels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `duels` (
  `duelid` varchar(32) DEFAULT NULL,
  `turn` varchar(15) DEFAULT NULL,
  `incoming` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `duels`
--

LOCK TABLES `duels` WRITE;
/*!40000 ALTER TABLE `duels` DISABLE KEYS */;
/*!40000 ALTER TABLE `duels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `players` (
  `name` varchar(255) NOT NULL,
  `id` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `players`
--

LOCK TABLES `players` WRITE;
/*!40000 ALTER TABLE `players` DISABLE KEYS */;
INSERT INTO `players` VALUES ('player','U123123'),('toph','<@U0D0ZLX36>'),('sam','<@U16DH6DDH>'),('richards','<@U220XSW95>'),('bella','<@U1SNK98CE>'),('jeremy','<@U0D0X1MUP>'),('libby','<@U2ETYRT4H>'),('chris','<@U0D12MZN2>'),('rich','<@U0D119WGM>'),('britt','<@U0W9EJ763>'),('lizzy','<@U40CGPML6>'),('bill','<@U409J0T6W>'),('danny','<@U3ZK6BND7>'),('ross','<@U0D1MK0CF>');
/*!40000 ALTER TABLE `players` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `mode` varchar(255) DEFAULT NULL,
  `player` varchar(20) DEFAULT NULL,
  `val` varchar(255) DEFAULT NULL,
  `pkey` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES ('GameOn','rich','12','str'),('GameOn','rich','900','Justice'),('scoop','chris','17','scoopability'),('scoop','bella','9','scoopability'),('scoop','matt','13','scoopability'),('scoop','bella','true','isAnIcecream'),('scoop','bella','chocolate','flavor'),('scoop','rich','16','scoopability'),('scoop','raw_dawg','4','scoopability'),('scoop','sam','19','scoopability'),('gladiator','matt','16','dex'),('gladiator','ross','10','dex'),('gladiator','armor','none','matt'),('gladiator','weapons','double_daggers','matt'),('gladiator','armor','iron','ross'),('gladiator','weapons','whip','ross'),('gladiator','matt','none','armor'),('gladiator','matt','double_daggers','weapons'),('gladiator','ross','iron','armor'),('gladiator','ross','whip','weapons'),('gladiator','bella','queen','status'),('gladiator','libby','ninja','status'),('gladiator','ross','13','con'),('gladiator','matt','12','con'),('gladiator','matt','35','hp'),('gladiator','ross','40','hp'),('gladiator','matt','35','max_hp'),('gladiator','ross','40','max_hp'),('gunz','bella','ak47','gun'),('gunz','rich','beretta','gun'),('gunz','topher','n/a','lunch'),('gunz','rich','home','lunch-location'),('wagers','bird','0','giphy');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats`
--

DROP TABLE IF EXISTS `stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats` (
  `val` varchar(255) DEFAULT NULL,
  `pkey` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats`
--

LOCK TABLES `stats` WRITE;
/*!40000 ALTER TABLE `stats` DISABLE KEYS */;
INSERT INTO `stats` VALUES ('18','giphy score');
/*!40000 ALTER TABLE `stats` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-02-08  9:28:27
