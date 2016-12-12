/*
Navicat MySQL Data Transfer

Source Server         : 1
Source Server Version : 50626
Source Host           : 127.0.0.1:3306
Source Database       : battleship

Target Server Type    : MYSQL
Target Server Version : 50626
File Encoding         : 65001

Date: 2016-12-12 19:24:21
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for map
-- ----------------------------
DROP TABLE IF EXISTS `map`;
CREATE TABLE `map` (
  `map_id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `rows` int(6) DEFAULT NULL COMMENT 'number of rows on this field',
  `columns` int(6) DEFAULT NULL COMMENT 'number of columns on this field',
  `game_started` int(1) DEFAULT '0' COMMENT '0 - not started yet, 1 - game started',
  PRIMARY KEY (`map_id`),
  KEY `map_ibfk_1` (`server_id`),
  CONSTRAINT `map_ibfk_1` FOREIGN KEY (`server_id`) REFERENCES `server` (`server_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of map
-- ----------------------------
INSERT INTO `map` VALUES ('74', '2', 'abc game', '39', '12', '12', '0');

-- ----------------------------
-- Table structure for player
-- ----------------------------
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
  `player_id` int(11) NOT NULL AUTO_INCREMENT,
  `nickname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player
-- ----------------------------
INSERT INTO `player` VALUES ('45', 'rrr');

-- ----------------------------
-- Table structure for player_hits
-- ----------------------------
DROP TABLE IF EXISTS `player_hits`;
CREATE TABLE `player_hits` (
  `shot_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_id` int(11) DEFAULT NULL,
  `row` int(11) DEFAULT NULL,
  `column` int(11) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `hit` int(11) DEFAULT NULL COMMENT 'If shot hit in someone = 1, otherwise 0',
  PRIMARY KEY (`shot_id`),
  KEY `player_hits_ibfk_1` (`map_id`),
  KEY `player_hits_ibfk_2` (`player_id`),
  CONSTRAINT `player_hits_ibfk_1` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `player_hits_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_hits
-- ----------------------------
INSERT INTO `player_hits` VALUES ('3', null, null, null, null, null, null);

-- ----------------------------
-- Table structure for player_to_map
-- ----------------------------
DROP TABLE IF EXISTS `player_to_map`;
CREATE TABLE `player_to_map` (
  `map_id` int(11) NOT NULL,
  `player_id` int(11) NOT NULL,
  `time_connected` datetime DEFAULT NULL,
  PRIMARY KEY (`map_id`,`player_id`),
  KEY `player_to_map_ibfk_3` (`player_id`),
  CONSTRAINT `player_to_map_ibfk_2` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `player_to_map_ibfk_3` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_to_map
-- ----------------------------

-- ----------------------------
-- Table structure for server
-- ----------------------------
DROP TABLE IF EXISTS `server`;
CREATE TABLE `server` (
  `server_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`server_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server
-- ----------------------------
INSERT INTO `server` VALUES ('1', 'server1');
INSERT INTO `server` VALUES ('2', 'server2');
INSERT INTO `server` VALUES ('3', '123');

-- ----------------------------
-- Table structure for ship_to_map
-- ----------------------------
DROP TABLE IF EXISTS `ship_to_map`;
CREATE TABLE `ship_to_map` (
  `location_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `player_id` int(11) NOT NULL,
  `row_start` int(5) DEFAULT NULL,
  `row_end` int(5) DEFAULT NULL,
  `column_start` int(5) DEFAULT NULL,
  `column_end` int(5) DEFAULT NULL,
  `ship_type` int(1) NOT NULL DEFAULT '1' COMMENT 'size of ship (''1'',''2'',''3'',''4'')',
  PRIMARY KEY (`location_id`),
  KEY `ship_to_map_ibfk_3` (`player_id`),
  KEY `ship_to_map_ibfk_4` (`map_id`),
  CONSTRAINT `ship_to_map_ibfk_3` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ship_to_map_ibfk_4` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=408 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of ship_to_map
-- ----------------------------
