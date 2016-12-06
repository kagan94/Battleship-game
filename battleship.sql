/*
Navicat MySQL Data Transfer

Source Server         : 1
Source Server Version : 50626
Source Host           : 127.0.0.1:3306
Source Database       : battleship

Target Server Type    : MYSQL
Target Server Version : 50626
File Encoding         : 65001

Date: 2016-12-07 00:51:24
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for invitation
-- ----------------------------
DROP TABLE IF EXISTS `invitation`;
CREATE TABLE `invitation` (
  `invitation_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `initiator_id` int(11) DEFAULT NULL COMMENT 'Player whi inizialized the invitation',
  `invited_player_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`invitation_id`),
  KEY `invitation_ibfk_1` (`initiator_id`),
  KEY `invitation_ibfk_2` (`invited_player_id`),
  KEY `invitation_ibfk_3` (`map_id`),
  CONSTRAINT `invitation_ibfk_1` FOREIGN KEY (`initiator_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `invitation_ibfk_2` FOREIGN KEY (`invited_player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `invitation_ibfk_3` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of invitation
-- ----------------------------

-- ----------------------------
-- Table structure for map
-- ----------------------------
DROP TABLE IF EXISTS `map`;
CREATE TABLE `map` (
  `map_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `rows` int(6) DEFAULT NULL COMMENT 'number of rows on this field',
  `columns` int(6) DEFAULT NULL COMMENT 'number of columns on this field',
  PRIMARY KEY (`map_id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of map
-- ----------------------------

-- ----------------------------
-- Table structure for player
-- ----------------------------
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
  `player_id` int(11) NOT NULL AUTO_INCREMENT,
  `nickname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player
-- ----------------------------
INSERT INTO `player` VALUES ('3', 'sdasds');
INSERT INTO `player` VALUES ('4', 'aaaaab');
INSERT INTO `player` VALUES ('5', 'aaaa1ab');
INSERT INTO `player` VALUES ('6', 'aaaab');
INSERT INTO `player` VALUES ('7', 'aaaab2');
INSERT INTO `player` VALUES ('8', 'aaaab23');
INSERT INTO `player` VALUES ('9', 'aaaab22');
INSERT INTO `player` VALUES ('10', '');

-- ----------------------------
-- Table structure for player_hits
-- ----------------------------
DROP TABLE IF EXISTS `player_hits`;
CREATE TABLE `player_hits` (
  `shot_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `player_id` int(11) NOT NULL,
  `row` int(5) NOT NULL,
  `column` int(5) NOT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  `hit` int(1) DEFAULT NULL COMMENT 'If shot hit in someone = 1, otherwise 0',
  PRIMARY KEY (`shot_id`,`map_id`,`player_id`),
  KEY `player_hits_ibfk_3` (`player_id`),
  KEY `player_hits_ibfk_2` (`map_id`),
  CONSTRAINT `player_hits_ibfk_2` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `player_hits_ibfk_3` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_hits
-- ----------------------------

-- ----------------------------
-- Table structure for player_to_map
-- ----------------------------
DROP TABLE IF EXISTS `player_to_map`;
CREATE TABLE `player_to_map` (
  `map_id` int(11) NOT NULL,
  `player_id` int(11) NOT NULL,
  PRIMARY KEY (`map_id`,`player_id`),
  KEY `player_to_map_ibfk_3` (`player_id`),
  CONSTRAINT `player_to_map_ibfk_2` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `player_to_map_ibfk_3` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_to_map
-- ----------------------------

-- ----------------------------
-- Table structure for ship_to_map
-- ----------------------------
DROP TABLE IF EXISTS `ship_to_map`;
CREATE TABLE `ship_to_map` (
  `map_id` int(11) NOT NULL,
  `player_id` int(11) NOT NULL,
  `row_start` int(5) DEFAULT NULL,
  `row_end` int(5) DEFAULT NULL,
  `column_start` int(5) DEFAULT NULL,
  `column_end` int(5) DEFAULT NULL,
  `ship_type` int(1) NOT NULL DEFAULT '1' COMMENT 'size of ship (''1'',''2'',''3'',''4'')',
  PRIMARY KEY (`map_id`,`player_id`,`ship_type`),
  KEY `ship_to_map_ibfk_3` (`player_id`),
  CONSTRAINT `ship_to_map_ibfk_2` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ship_to_map_ibfk_3` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of ship_to_map
-- ----------------------------
